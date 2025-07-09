// 声明markdown-it模块
declare module 'markdown-it' {
  interface MarkdownIt {
    render(content: string): string;
    utils: {
      escapeHtml(content: string): string;
    };
  }
  
  export default function markdownit(options?: any): MarkdownIt;
} 