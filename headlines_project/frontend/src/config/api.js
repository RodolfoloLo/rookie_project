/**
 * API配置文件
 * 包含API基础URL和AI问答功能所需的API参数
 */

// API基础URL配置
export const apiConfig = {
  // 开发环境默认走本机后端，生产环境默认走同域反向代理
  baseURL: import.meta.env.VITE_API_BASE_URL || (import.meta.env.PROD ? '/api' : 'http://127.0.0.1:8000'),
}

export const aiChatConfig = {
  // DashScope API地址
  apiEndpoint: import.meta.env.VITE_AI_API_ENDPOINT || 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
  
  // API Key 必须通过环境变量注入
  apiKey: import.meta.env.VITE_DASHSCOPE_API_KEY || '',
  
  // 使用的模型
  model: import.meta.env.VITE_AI_MODEL || 'qwen3-max-preview'
}
