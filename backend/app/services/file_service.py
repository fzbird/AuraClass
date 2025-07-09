from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import FileResponse
import tempfile
from urllib.parse import quote

from app.utils.file_handlers import (
    FileHandler, 
    StudentImportHandler,
    QuantRecordImportHandler
)
from app.crud.student import student as student_crud
from app.crud.quant_record import quant_record_crud
from app.schemas.student import StudentCreate
from app.schemas.quant_record import QuantRecordCreate

class FileService:
    @staticmethod
    async def import_students(
        db: AsyncSession,
        file: UploadFile,
        current_user_id: int
    ) -> Tuple[int, List[str]]:
        """导入学生数据"""
        # 定义中文表头映射
        header_map = {
            "student_id_no": "学号",
            "full_name": "姓名",
            "class_id": "班级ID",
            "gender": "性别",
            "birth_date": "出生日期",
            "contact_info": "联系方式"
        }
        
        # 检查文件类型并处理
        if file.filename.endswith('.csv'):
            data = await FileHandler.process_csv_upload(file, header_map)
        elif file.filename.endswith(('.xlsx', '.xls')):
            data = await FileHandler.process_excel_upload(file, header_map)
        else:
            raise HTTPException(
                status_code=400,
                detail="不支持的文件格式，请上传CSV或Excel文件"
            )
        
        # 验证数据
        validated_data, errors = StudentImportHandler.validate_student_data(data)
        
        if not validated_data:
            raise HTTPException(
                status_code=400,
                detail=f"数据验证失败: {'; '.join(errors)}"
            )
        
        # 导入数据
        success_count = 0
        for row in validated_data:
            try:
                student_in = StudentCreate(
                    student_id_no=row['student_id_no'],
                    full_name=row['full_name'],
                    class_id=row['class_id'],
                    created_by=current_user_id
                )
                await student_crud.create(db, obj_in=student_in)
                success_count += 1
            except Exception as e:
                errors.append(f"导入学生 {row['student_id_no']} 失败: {str(e)}")
        
        return success_count, errors

    @staticmethod
    async def import_quant_records(
        db: AsyncSession,
        file: UploadFile,
        current_user_id: int
    ) -> Tuple[int, List[str]]:
        """导入量化记录数据"""
        # 定义中文表头映射
        header_map = {
            "student_id": "学生ID",
            "item_id": "量化项目ID",
            "score": "分数",
            "reason": "原因",
            "record_date": "记录日期"
        }
        
        # 检查文件类型并处理
        if file.filename.endswith('.csv'):
            data = await FileHandler.process_csv_upload(file, header_map)
        elif file.filename.endswith(('.xlsx', '.xls')):
            data = await FileHandler.process_excel_upload(file, header_map)
        else:
            raise HTTPException(
                status_code=400,
                detail="不支持的文件格式，请上传CSV或Excel文件"
            )
        
        # 验证数据
        validated_data, errors = QuantRecordImportHandler.validate_quant_record_data(data)
        
        if not validated_data:
            raise HTTPException(
                status_code=400,
                detail=f"数据验证失败: {'; '.join(errors)}"
            )
        
        # 导入数据
        success_count = 0
        for row in validated_data:
            try:
                record_in = QuantRecordCreate(
                    student_id=row['student_id'],
                    item_id=row['item_id'],
                    score=row['score'],
                    reason=row.get('reason'),
                    record_date=row['record_date'],
                    recorder_id=current_user_id
                )
                await quant_record_crud.create(db, obj_in=record_in)
                success_count += 1
            except Exception as e:
                errors.append(f"导入记录失败: {str(e)}")
        
        return success_count, errors

    @staticmethod
    def export_data(
        data: List[Dict[str, Any]],
        headers: Dict[str, str],
        filename_prefix: str,
        format: str = "csv"
    ):
        """
        导出数据为指定格式
        
        Args:
            data: 要导出的数据
            headers: 列头映射，字段名与显示名的映射
            filename_prefix: 文件名前缀
            format: 导出格式，支持 csv 和 excel
        
        Returns:
            FileResponse 对象
        """
        try:
            # 添加时间戳到文件名前缀
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            final_filename_prefix = f"{filename_prefix}_{timestamp}"
            
            if format == "csv":
                filename, content = FileHandler.export_to_csv(data, headers, final_filename_prefix)
                media_type = "application/octet-stream"
            elif format == "excel":
                filename, content = FileHandler.export_to_excel(data, headers, final_filename_prefix)
                media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            else:
                raise HTTPException(
                    status_code=400,
                    detail="不支持的导出格式"
                )
                
            # 创建临时文件 - 使用二进制模式确保不会有编码转换
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format}", mode="wb") as temp:
                temp.write(content)
                temp_path = temp.name
            
            # 创建响应
            response = FileResponse(
                path=temp_path,
                filename=filename,
                media_type=media_type,
                background=None  # 文件发送后自动删除
            )
            
            # 特别处理Content-Disposition头，确保文件名正确
            # URL编码文件名，解决中文文件名问题
            encoded_filename = quote(filename)
            response.headers["Content-Disposition"] = f'attachment; filename="{encoded_filename}"; filename*=UTF-8\'\'{encoded_filename}'
            
            # 阻止内容嗅探
            response.headers["X-Content-Type-Options"] = "nosniff"
            
            # 如果是CSV，添加特殊的编码头
            if format == "csv":
                # 告诉浏览器不要猜测编码
                response.headers["Content-Type"] = "application/octet-stream"
                # 特别针对中文添加编码指示
                response.headers["X-Content-Encoding"] = "GB18030"  # 自定义头，提示客户端
            
            return response
        except Exception as e:
            # 记录详细错误
            import traceback
            error_msg = f"文件导出失败: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            raise HTTPException(
                status_code=500,
                detail=f"文件导出失败: {str(e)}"
            )
