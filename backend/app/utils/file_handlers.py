from typing import List, Dict, Any, Optional, BinaryIO, Tuple, Union
import csv
import json
import tempfile
from pathlib import Path
from datetime import datetime
import xlsxwriter
from openpyxl import load_workbook, Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import pandas as pd
from fastapi import UploadFile, HTTPException
from fastapi.responses import FileResponse
import io

class FileHandler:
    """文件处理基类"""
    
    @staticmethod
    async def read_csv(file: UploadFile) -> List[Dict[str, Any]]:
        """读取CSV文件，支持多种编码格式"""
        try:
            content = await file.read()
            
            # 尝试不同的编码格式，优先考虑中文环境常用的编码
            encodings_to_try = ['gb18030', 'gbk', 'utf-8', 'utf-8-sig']
            
            # 先检测并处理BOM标记
            if content.startswith(b'\xef\xbb\xbf'):  # UTF-8 BOM
                content = content[3:]
                encodings_to_try = ['utf-8', 'utf-8-sig'] + [e for e in encodings_to_try if e not in ['utf-8', 'utf-8-sig']]
            
            # 尝试不同编码
            text = None
            for encoding in encodings_to_try:
                try:
                    text = content.decode(encoding)
                    print(f"成功使用{encoding}编码解析CSV")
                    break
                except UnicodeDecodeError:
                    continue
            
            if text is None:
                # 如果所有编码都失败，使用替换错误的方式强制解码
                text = content.decode('utf-8', errors='replace')
                print("无法正确识别CSV编码，使用替代符号解码")
            
            # 解析CSV内容
            csv_reader = csv.DictReader(io.StringIO(text))
            rows = []
            for row in csv_reader:
                # 清理数据：移除键和值的空白，跳过空行
                cleaned_row = {}
                for key, value in row.items():
                    if key is not None:  # 有些CSV可能有空列头
                        cleaned_key = key.strip() if isinstance(key, str) else key
                        cleaned_value = value.strip() if isinstance(value, str) else value
                        cleaned_row[cleaned_key] = cleaned_value
                
                # 只添加非空行
                if any(cleaned_row.values()):
                    rows.append(cleaned_row)
            
            return rows
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"CSV文件读取失败: {str(e)}"
            )

    @staticmethod
    async def read_excel(file: UploadFile) -> List[Dict[str, Any]]:
        """读取Excel文件"""
        try:
            content = await file.read()
            
            # 使用pandas读取Excel文件，增加错误处理
            try:
                df = pd.read_excel(io.BytesIO(content), dtype=str)
                
                # 处理NaN值，转换为None
                df = df.replace({pd.NA: None})
                df = df.where(pd.notna(df), None)
                
                # 确保所有列名为字符串类型
                df.columns = df.columns.astype(str)
                
                # 自动清除列名两端空白
                df.columns = df.columns.str.strip()
                
                # 为所有字符串列清除两端空白
                for col in df.select_dtypes(include=['object']).columns:
                    df[col] = df[col].str.strip() if df[col].dtype == 'object' else df[col]
                
                return df.to_dict('records')
            except Exception as inner_e:
                raise Exception(f"Excel格式错误: {str(inner_e)}")
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Excel文件读取失败: {str(e)}"
            )

    @staticmethod
    def export_to_csv(
        data: List[Dict[str, Any]], 
        headers: Dict[str, str],
        filename: str
    ) -> Tuple[str, bytes]:
        """
        导出数据到CSV文件，使用GB18030编码以确保在Windows Excel中正确显示中文
        
        Args:
            data: 要导出的数据列表
            headers: 表头映射，键为字段名，值为表头显示名
            filename: 文件名前缀
        
        Returns:
            包含文件名和内容的元组
        """
        try:
            # 使用内存缓冲区
            with io.StringIO() as buffer:
                # 使用Excel方言，避免自定义分隔符可能导致的问题
                writer = csv.writer(buffer, dialect='excel')
                
                # 写入表头
                writer.writerow(headers.values())
                
                # 写入数据
                if data:
                    for row in data:
                        row_data = []
                        # 按headers的顺序处理每个字段
                        for field in headers.keys():
                            value = row.get(field, "")
                            # 处理数值类型
                            if isinstance(value, float):
                                value = f"{value:.2f}"
                            elif isinstance(value, int):
                                value = str(value)
                            # 处理None值
                            elif value is None:
                                value = ""
                            # 其他值转为字符串
                            else:
                                value = str(value)
                            row_data.append(value)
                        writer.writerow(row_data)
                
                # 获取CSV内容
                csv_content = buffer.getvalue()
                
                # 使用GB18030编码（Windows Excel完全兼容的中文编码）
                # 不使用UTF-8，因为Windows Excel对UTF-8的支持不一致
                encoded_content = csv_content.encode('gb18030')
                
                return (f"{filename}.csv", encoded_content)
        
        except Exception as e:
            import traceback
            error_msg = f"CSV导出失败: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            raise HTTPException(
                status_code=500,
                detail=f"CSV导出失败: {str(e)}"
            )

    @staticmethod
    def export_to_excel(
        data: List[Dict[str, Any]],
        headers: Dict[str, str],
        filename: str,
        sheet_name: str = "Sheet1"
    ) -> Tuple[str, bytes]:
        """
        导出数据到Excel文件
        
        Args:
            data: 要导出的数据列表
            headers: 表头映射，键为字段名，值为表头显示名
            filename: 文件名前缀
            sheet_name: 工作表名称
        
        Returns:
            包含文件名和内容的元组
        """
        try:
            # 创建一个内存中的输出流
            output = io.BytesIO()
            
            # 创建工作簿和工作表
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet(sheet_name)
            
            # 设置表头样式
            header_format = workbook.add_format({
                'bold': True,
                'font_name': 'Microsoft YaHei',  # 使用微软雅黑，更好的中文支持
                'align': 'center',
                'valign': 'vcenter',
                'border': 1
            })
            
            # 设置内容样式
            content_format = workbook.add_format({
                'font_name': 'Microsoft YaHei',
                'align': 'left',
                'valign': 'vcenter',
            })
            
            # 设置数字格式
            number_format = workbook.add_format({
                'font_name': 'Microsoft YaHei',
                'align': 'right',
                'valign': 'vcenter',
                'num_format': '0.00'  # 两位小数
            })
            
            # 添加表头
            fieldnames = list(headers.values())
            for col_idx, header in enumerate(fieldnames):
                worksheet.write(0, col_idx, header, header_format)
            
            # 如果没有数据则返回
            if not data:
                workbook.close()
                output.seek(0)
                return (f"{filename}.xlsx", output.getvalue())
            
            # 转换数据并写入工作表
            row_idx = 1  # 从第二行开始写数据
            for item in data:
                col_idx = 0
                for field_name, header in headers.items():
                    value = item.get(field_name)
                    
                    # 根据值类型选择不同的格式
                    if isinstance(value, (float, int)):
                        worksheet.write(row_idx, col_idx, float(value), number_format)
                    elif value is None:
                        worksheet.write(row_idx, col_idx, "", content_format)
                    else:
                        worksheet.write(row_idx, col_idx, str(value), content_format)
                        
                    col_idx += 1
                row_idx += 1
            
            # 自动调整列宽
            for col_idx, _ in enumerate(fieldnames):
                # 设置列宽为表头长度的1.5倍，最小12字符
                header_length = len(fieldnames[col_idx]) * 1.5
                worksheet.set_column(col_idx, col_idx, max(12, header_length))
            
            # 关闭工作簿并获取输出
            workbook.close()
            output.seek(0)
            
            return (f"{filename}.xlsx", output.getvalue())
            
        except Exception as e:
            # 记录详细错误
            import traceback
            error_msg = f"Excel导出失败: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            
            raise HTTPException(
                status_code=500,
                detail=f"Excel导出失败: {str(e)}"
            )

    @staticmethod
    async def process_csv_upload(file: UploadFile, header_map: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        处理CSV文件上传
        
        Args:
            file: 上传的文件
            header_map: 可选的表头映射，键为中文表头，值为字段名
        """
        data = await FileHandler.read_csv(file)
        
        # 如果提供了表头映射，转换中文表头为字段名
        if header_map and data:
            converted_data = []
            for row in data:
                converted_row = {}
                for zh_key, value in row.items():
                    # 查找中文表头对应的字段名
                    for field_name, zh_header in header_map.items():
                        if zh_header == zh_key:
                            converted_row[field_name] = value
                            break
                    else:
                        # 如果没有找到匹配，保留原键
                        converted_row[zh_key] = value
                converted_data.append(converted_row)
            return converted_data
            
        return data
    
    @staticmethod
    async def process_excel_upload(file: UploadFile, header_map: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        处理Excel文件上传
        
        Args:
            file: 上传的文件
            header_map: 可选的表头映射，键为中文表头，值为字段名
        """
        data = await FileHandler.read_excel(file)
        
        # 如果提供了表头映射，转换中文表头为字段名
        if header_map and data:
            converted_data = []
            for row in data:
                converted_row = {}
                for zh_key, value in row.items():
                    # 查找中文表头对应的字段名
                    for field_name, zh_header in header_map.items():
                        if zh_header == zh_key:
                            converted_row[field_name] = value
                            break
                    else:
                        # 如果没有找到匹配，保留原键
                        converted_row[zh_key] = value
                converted_data.append(converted_row)
            return converted_data
            
        return data

class DataValidator:
    """数据验证基类"""
    
    @staticmethod
    def validate_required_fields(
        data: Dict[str, Any],
        required_fields: List[str]
    ) -> List[str]:
        """验证必填字段"""
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                missing_fields.append(field)
        return missing_fields

    @staticmethod
    def validate_field_type(
        value: Any,
        field_type: type,
        field_name: str
    ) -> Optional[str]:
        """验证字段类型"""
        try:
            field_type(value)
            return None
        except (ValueError, TypeError):
            return f"字段 {field_name} 的值 {value} 不是有效的 {field_type.__name__} 类型"

class StudentDataValidator(DataValidator):
    """学生数据验证器"""
    
    REQUIRED_FIELDS = ["student_id", "name", "class_id"]
    
    @classmethod
    def validate(cls, data: Dict[str, Any]) -> List[str]:
        """验证学生数据"""
        errors = []
        
        # 验证必填字段
        missing_fields = cls.validate_required_fields(data, cls.REQUIRED_FIELDS)
        if missing_fields:
            errors.append(f"缺少必填字段: {', '.join(missing_fields)}")
        
        # 验证字段类型
        if "student_id" in data:
            type_error = cls.validate_field_type(data["student_id"], str, "student_id")
            if type_error:
                errors.append(type_error)
                
        if "class_id" in data:
            type_error = cls.validate_field_type(data["class_id"], int, "class_id")
            if type_error:
                errors.append(type_error)
        
        return errors

class QuantRecordDataValidator(DataValidator):
    """量化记录数据验证器"""
    
    REQUIRED_FIELDS = ["student_id", "item_id", "score"]
    
    @classmethod
    def validate(cls, data: Dict[str, Any]) -> List[str]:
        """验证量化记录数据"""
        errors = []
        
        # 验证必填字段
        missing_fields = cls.validate_required_fields(data, cls.REQUIRED_FIELDS)
        if missing_fields:
            errors.append(f"缺少必填字段: {', '.join(missing_fields)}")
        
        # 验证字段类型
        if "score" in data:
            type_error = cls.validate_field_type(data["score"], float, "score")
            if type_error:
                errors.append(type_error)
                
        if "item_id" in data:
            type_error = cls.validate_field_type(data["item_id"], int, "item_id")
            if type_error:
                errors.append(type_error)
        
        return errors

class StudentImportHandler:
    @staticmethod
    def validate_student_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """验证学生数据格式"""
        required_fields = {'student_id_no', 'full_name', 'class_id'}
        validated_data = []
        errors = []
        
        for idx, row in enumerate(data, start=1):
            # 检查必填字段
            missing_fields = required_fields - set(row.keys())
            if missing_fields:
                errors.append(f"第{idx}行缺少必填字段: {', '.join(missing_fields)}")
                continue
            
            # 验证学号格式
            if not row['student_id_no'].strip():
                errors.append(f"第{idx}行学号不能为空")
                continue
            
            # 验证姓名
            if not row['full_name'].strip():
                errors.append(f"第{idx}行姓名不能为空")
                continue
            
            # 验证班级ID
            try:
                row['class_id'] = int(row['class_id'])
            except (ValueError, TypeError):
                errors.append(f"第{idx}行班级ID必须是数字")
                continue
            
            validated_data.append(row)
        
        return validated_data, errors

class QuantRecordImportHandler:
    @staticmethod
    def validate_quant_record_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """验证量化记录数据格式"""
        required_fields = {'student_id', 'item_id', 'score', 'record_date'}
        validated_data = []
        errors = []
        
        for idx, row in enumerate(data, start=1):
            # 检查必填字段
            missing_fields = required_fields - set(row.keys())
            if missing_fields:
                errors.append(f"第{idx}行缺少必填字段: {', '.join(missing_fields)}")
                continue
            
            # 验证分数
            try:
                row['score'] = float(row['score'])
                if not 0 <= row['score'] <= 100:
                    errors.append(f"第{idx}行分数必须在0-100之间")
                    continue
            except (ValueError, TypeError):
                errors.append(f"第{idx}行分数必须是数字")
                continue
            
            # 验证日期格式
            try:
                datetime.strptime(row['record_date'], '%Y-%m-%d')
            except ValueError:
                errors.append(f"第{idx}行日期格式错误，应为YYYY-MM-DD")
                continue
            
            validated_data.append(row)
        
        return validated_data, errors
