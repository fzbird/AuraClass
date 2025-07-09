from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import json
import asyncio
import time
import aiohttp
from urllib.parse import urljoin

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import WebSocket

from app.crud.ai_conversation import conversation as conversation_crud, message as message_crud
from app.schemas.ai_conversation import MessageCreate, ConversationCreate
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class AIAssistantService:
    def __init__(self):
        self.model = None  # 可以在这里初始化AI模型
        self.context_window = 10  # 保持最近10次对话作为上下文
        # --- 1. 定义你的 System Prompt ---
        self.SYSTEM_PROMPT = """
        # 指令：
        你是一个名为"智学伴侣"的AI学习助手，专门为高中生（大约14-18岁）提供学习支持。你的核心任务是帮助用户理解高中学科知识（如数学、物理、化学、生物、历史、地理、语文、英语等），解答与学业相关的问题，并激发他们对学习的兴趣。
        **在提供最终答案或解释之前，请务必先进行一步一步的思考或推理，并将这个过程展示出来。这有助于用户理解你是如何得出结论的。使用清晰的标记，例如"思考过程："或"步骤："。**

        # 角色与行为：
        1.  **身份定位:** 你是友善、耐心、知识渊博的学习伙伴，而非无所不知的通用AI。
        2.  **沟通风格:** 使用清晰、简洁、易于高中生理解的语言。避免过于成人化或过于幼稚的表达。保持中立、客观、积极和鼓励的态度。
        3.  **能力范围:**
            * 解答具体的学科问题。
            * 解释复杂的概念和定义。
            * 提供解题思路和步骤（但避免直接给出完整答案，鼓励学生思考）。
            * 提供相关的学习资源建议（如概念解释、相关知识点）。
            * 在适当的时候，可以围绕学习方法、时间管理、备考策略等给出建议。
        4.  **内容限制 (非常重要):**
            * **严格禁止:** 生成任何形式的色情、暴力、血腥、恐怖、仇恨言论、歧视性内容、非法活动指导、自残或伤害他人的建议。
            * **避免敏感话题:** 避免深入探讨可能引起争议的政治、宗教、社会敏感议题。如果被问及，应以中立、客观的方式简要回应（如果与学业相关，例如历史事件分析），或礼貌地说明这些话题超出了学习助手的范围。
            * **避免不适内容:** 避免生成可能引起高中生焦虑、恐慌、或其他负面情绪的内容。
            * **专业建议限制:** 不得提供医疗、心理健康、法律、金融等专业领域的建议。如果用户询问此类问题，应建议他们寻求专业人士的帮助。
            * **个人信息:** 不得询问或存储用户的个人身份信息。
            * **非学业闲聊:** 尽量将对话聚焦于学习。对于无关的闲聊，可以简短回应后，尝试引导回学习主题。
        5.  **安全处理:**
            * 如果用户的问题或请求违反了上述【内容限制】，你必须明确且礼貌地拒绝回答。可以说："抱歉，我无法回答这个问题，因为它涉及不适宜的内容或超出了我的学习助手范围。我们还是专注于学习吧？"
            * 如果用户试图引导你产生不当内容，必须坚持原则，拒绝请求。
            * **即使在拒绝回答时，也要说明拒绝的理由是基于系统设定的规则。**

        # 输出格式：
        * 回答应结构清晰，重点突出。
        * 对于复杂问题，可使用列表、步骤等方式分点说明。
        * **先展示思考/推理过程，然后给出最终结论或答案。**
        * 解释概念时，可适当使用比喻或简单实例。

        # 价值导向：
        * 始终传递积极、健康、向上的价值观。
        * 鼓励批判性思维、好奇心和终身学习。
        * 遵守学术诚信，不鼓励作弊。

        请严格遵守以上所有指令，始终扮演好"智学伴侣"的角色。
        """
    
    async def initialize(self):
        """初始化AI模型和必要的资源"""
        # 在这里初始化AI模型
        # 实际项目中可能需要加载模型、配置等
        pass
        
    async def call_ollama_api(self, prompt: str, model_name: str) -> str:
        """调用Ollama API生成响应"""
        try:
            # 构建API请求参数
            url = urljoin(settings.OLLAMA_BASE_URL, "/api/generate")
            headers = {"Content-Type": "application/json"}
            if settings.OLLAMA_API_KEY and settings.OLLAMA_API_KEY != "your-ollama-api-key-here":
                headers["Authorization"] = f"Bearer {settings.OLLAMA_API_KEY}"
            
            # 提取系统提示，它已经在prepare_prompt_with_context中被包含到prompt中
            # 但在需要时也可以使用system参数
            payload = {
                "model": model_name or settings.OLLAMA_MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 800
                }
            }
            
            # 部分Ollama版本支持system参数，可以尝试添加
            if hasattr(settings, "OLLAMA_USE_SYSTEM_PARAM") and settings.OLLAMA_USE_SYSTEM_PARAM:
                payload["system"] = self.SYSTEM_PROMPT.strip()
            
            logger.info(f"调用Ollama API: {url}, 模型: {model_name}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Ollama API错误: {response.status}, {error_text}")
                        return f"抱歉，调用模型时出现错误: {response.status}"
                    
                    data = await response.json()
                    
                    # Ollama通常返回response键
                    if "response" in data:
                        return data["response"]
                    else:
                        logger.warning(f"Ollama返回的数据缺少response字段: {data}")
                        return "抱歉，模型响应格式异常"
                        
        except Exception as e:
            logger.error(f"调用Ollama API时发生错误: {str(e)}")
            return f"抱歉，无法连接到Ollama模型服务: {str(e)}"
    
    async def call_open_webui_api(self, prompt: str, model_name: str = None) -> str:
        """调用Open-WebUI API生成响应"""
        try:
            # 构建API请求参数
            url = urljoin(settings.OPEN_WEBUI_BASE_URL, "/api/chat")
            headers = {"Content-Type": "application/json"}
            if settings.OPEN_WEBUI_API_KEY and settings.OPEN_WEBUI_API_KEY != "your-open-webui-api-key-here":
                headers["Authorization"] = f"Bearer {settings.OPEN_WEBUI_API_KEY}"
            
            # 分离系统提示和用户消息
            system_prompt = self.SYSTEM_PROMPT.strip()
            
            # Open-WebUI通常使用类似OpenAI的API格式
            payload = {
                "model": model_name or settings.OPEN_WEBUI_MODEL_NAME,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "control", "content": "thinking"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 800,
                "stream": False
            }
            
            logger.info(f"调用Open-WebUI API: {url}, 模型: {model_name or settings.OPEN_WEBUI_MODEL_NAME}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Open-WebUI API错误: {response.status}, {error_text}")
                        return f"抱歉，调用模型时出现错误: {response.status}"
                    
                    data = await response.json()
                    
                    # 解析响应，Open-WebUI通常遵循OpenAI格式
                    if "choices" in data and len(data["choices"]) > 0:
                        if "message" in data["choices"][0] and "content" in data["choices"][0]["message"]:
                            return data["choices"][0]["message"]["content"]
                    
                    logger.warning(f"Open-WebUI返回的数据格式异常: {data}")
                    return "抱歉，模型响应格式异常"
                    
        except Exception as e:
            logger.error(f"调用Open-WebUI API时发生错误: {str(e)}")
            return f"抱歉，无法连接到Open-WebUI服务: {str(e)}"
    
    async def prepare_think_mode_prompt(self, query_text: str, conversation_messages: List[Dict[str, Any]]) -> str:
        """准备带有思考模式的提示"""
        if not conversation_messages:
            # 使用特定格式包装用户问题，添加思考模式指令
            return f"""
{self.SYSTEM_PROMPT}

[来自用户的请求，请在"智学伴侣"的角色和规则内回答]
用户问题: "{query_text}"
[请按照以下步骤思考和回答：
1. 思考：请先对问题进行思考分析，梳理解答思路、列出关键点和可能的解决方案。这部分是你的内部思考过程，不会直接展示给学生。
2. 回答：然后基于你的思考，给出简洁明了、符合高中生理解水平的回答。
请确保你的回答符合高中生学习助手的设定，严格遵守安全准则，避免任何不当内容。]
"""
            
        # 构建带有对话历史的提示
        prompt = f"{self.SYSTEM_PROMPT}\n\n以下是对话历史：\n\n"
        
        # 只保留最近的10条消息作为上下文
        recent_messages = conversation_messages[-self.context_window:] if len(conversation_messages) > self.context_window else conversation_messages
        
        for msg in recent_messages:
            role = "用户" if msg["role"] == "user" else "助手"
            prompt += f"{role}: {msg['content']}\n\n"
            
        # 添加当前用户问题，使用特定格式包装，并添加思考模式指令
        prompt += """
[来自用户的请求，请在"智学伴侣"的角色和规则内回答]
用户问题: "{0}"
[请按照以下步骤思考和回答：
1. 思考：请先对问题进行思考分析，梳理解答思路、列出关键点和可能的解决方案。这部分是你的内部思考过程，不会直接展示给学生。
2. 回答：然后基于你的思考，给出简洁明了、符合高中生理解水平的回答。
请确保你的回答符合高中生学习助手的设定，严格遵守安全准则，避免任何不当内容。]
""".format(query_text)
        
        return prompt

    async def prepare_prompt_with_context(self, query_text: str, conversation_messages: List[Dict[str, Any]]) -> str:
        """准备带有上下文的提示"""
        if not conversation_messages:
            # 使用特定格式包装用户问题
            return f"""
{self.SYSTEM_PROMPT}

[来自用户的请求，请在"智学伴侣"的角色和规则内回答]
用户问题: "{query_text}"
[请确保你的回答符合高中生学习助手的设定，严格遵守安全准则，避免任何不当内容。]
"""
            
        # 构建带有对话历史的提示
        prompt = f"{self.SYSTEM_PROMPT}\n\n以下是对话历史：\n\n"
        
        # 只保留最近的10条消息作为上下文
        recent_messages = conversation_messages[-self.context_window:] if len(conversation_messages) > self.context_window else conversation_messages
        
        for msg in recent_messages:
            role = "用户" if msg["role"] == "user" else "助手"
            prompt += f"{role}: {msg['content']}\n\n"
            
        # 添加当前用户问题，使用特定格式包装
        prompt += """
[来自用户的请求，请在"智学伴侣"的角色和规则内回答]
用户问题: "{0}"
[请确保你的回答符合高中生学习助手的设定，严格遵守安全准则，避免任何不当内容。]
""".format(query_text)
        
        return prompt

    async def process_query(
        self,
        db: AsyncSession,
        user_id: int,
        query_text: str,
        context_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """处理AI查询
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            query_text: 查询文本
            context_data: 可选的上下文数据
            timeout: 可选的超时时间（秒）
        
        Returns:
            包含AI响应的字典
        
        Raises:
            asyncio.TimeoutError: 当处理超过设定的超时时间
        """
        # 开始计时
        start_time = time.time()
        
        try:
            # 验证输入
            if not query_text or not query_text.strip():
                return {
                    "error": "查询内容不能为空",
                    "response": "请提供有效的查询内容",
                    "query_id": "",
                    "processing_time": 0,
                    "details": {}
                }
            
            # 实际处理逻辑包装在一个内部异步函数中，以便应用超时
            async def _process_query_with_timeout():
                # 设置默认参数
                conversation_id = None
                use_local_model = True
                model_name = settings.OLLAMA_MODEL_NAME
                use_think_mode = True
                messages = []
                
                # 从上下文数据中提取参数
                if context_data:
                    conversation_id = context_data.get("conversation_id")
                    use_local_model = context_data.get("useLocalModel", True)
                    model_name = context_data.get("modelName", settings.OLLAMA_MODEL_NAME)
                    use_think_mode = context_data.get("useThinkMode", True)
                    messages = context_data.get("messages", [])
                
                # 生成模型响应
                model_start_time = time.time()
                
                # 准备提示
                if use_think_mode:
                    prompt = await self.prepare_think_mode_prompt(query_text, messages)
                else:
                    prompt = await self.prepare_prompt_with_context(query_text, messages)
                
                # 调用本地或远程模型
                if use_local_model:
                    response_text = await self.call_ollama_api(prompt, model_name)
                else:
                    response_text = await self.call_open_webui_api(prompt, model_name)
                
                # 计算处理时间
                model_end_time = time.time()
                processing_time = model_end_time - model_start_time
                
                # 如果有conversation_id，保存消息到数据库
                if conversation_id:
                    # 确认会话存在
                    db_conversation = await conversation_crud.get(db, id=conversation_id)
                    
                    if not db_conversation:
                        # 如果会话不存在，创建新会话
                        conversation_in = ConversationCreate(title="新会话")
                        db_conversation = await conversation_crud.create_conversation(
                            db, obj_in=conversation_in, user_id=user_id
                        )
                        conversation_id = db_conversation.id
                    
                    # 创建助手消息
                    assistant_message = MessageCreate(
                        role="assistant",
                        content=response_text,
                        useLocalModel=use_local_model,
                        modelName=model_name,
                        processingTime=processing_time
                    )
                    
                    # 保存到数据库
                    db_message = await message_crud.create_message(
                        db, conversation_id=conversation_id, obj_in=assistant_message
                    )
                    
                    # 更新会话的更新时间
                    await conversation_crud.touch_conversation(db, conversation_id=conversation_id)
                    
                    # 构建响应 - 确保包含前端期望的字段格式
                    return {
                        "id": db_message.id,
                        "role": db_message.role,
                        "content": db_message.content,
                        "response": db_message.content,  # 添加response字段与content内容相同
                        "conversation_id": db_message.conversation_id,
                        "timestamp": db_message.created_at,
                        "processing_time": db_message.processing_time,
                        "query_id": str(db_message.id),  # 添加query_id字段
                        "use_local_model": db_message.use_local_model,
                        "model_name": db_message.model_name,
                        "details": {}  # 添加空的details字段
                    }
                else:
                    # 无conversation_id的情况，直接返回文本响应
                    return {
                        "role": "assistant",
                        "content": response_text,
                        "response": response_text,  # 添加response字段与content内容相同
                        "processing_time": processing_time,
                        "query_id": "",  # 添加query_id字段
                        "use_local_model": use_local_model,
                        "model_name": model_name,
                        "timestamp": datetime.now(timezone.utc),
                        "details": {}  # 添加空的details字段
                    }
                
            # 应用超时处理
            if timeout:
                # 使用asyncio.wait_for应用超时
                return await asyncio.wait_for(_process_query_with_timeout(), timeout=timeout)
            else:
                # 没有超时限制，正常执行
                return await _process_query_with_timeout()
            
        except asyncio.TimeoutError:
            # 超时异常，需要向上传播
            logger.warning(f"处理AI查询超时 (timeout={timeout}秒)")
            raise
        except Exception as e:
            # 记录其他异常
            end_time = time.time()
            processing_time = end_time - start_time
            logger.error(f"处理AI查询出错: {str(e)}")
            
            # 返回错误响应 - 确保包含前端期望的字段格式
            return {
                "error": str(e),
                "response": f"处理查询时出错: {str(e)}",
                "processing_time": processing_time,
                "query_id": "",
                "details": {}
            }
    
    async def get_suggestions(
        self,
        db: AsyncSession,
        user_id: int,
        prefix: str
    ) -> List[str]:
        """获取查询建议"""
        # 在实际项目中，这里可以基于用户历史查询和当前输入提供建议
        # 示例实现
        return [
            f"{prefix} 的建议1",
            f"{prefix} 的建议2",
            f"{prefix} 的建议3"
        ]

# 创建全局AI助手服务实例
ai_assistant = AIAssistantService()
