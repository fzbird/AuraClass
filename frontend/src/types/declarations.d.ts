declare module 'naive-ui';
declare module '@vicons/antd/*';
declare module '@vicons/ionicons5/*';

// markdown-it模块声明
declare module 'markdown-it' {
  interface MarkdownIt {
    render(content: string): string;
    utils: {
      escapeHtml(content: string): string;
    };
  }
  
  export default function markdownit(options?: any): MarkdownIt;
}

// 为Vue组件添加类型声明
declare module '*.vue' {
  import type { DefineComponent } from 'vue';
  const component: DefineComponent<{}, {}, any>;
  export default component;
}

// 为静态资源添加类型声明
declare module '*.svg' {
  const content: string;
  export default content;
}

declare module '*.png' {
  const content: string;
  export default content;
}

declare module '*.jpg' {
  const content: string;
  export default content;
}

declare module '*.jpeg' {
  const content: string;
  export default content;
}

declare module '*.gif' {
  const content: string;
  export default content;
}

// 为CSS模块添加类型声明
declare module '*.css' {
  const classes: { [key: string]: string };
  export default classes;
}

declare module '*.scss' {
  const classes: { [key: string]: string };
  export default classes;
}

declare module '*.sass' {
  const classes: { [key: string]: string };
  export default classes;
}

// 为测试工具添加类型声明
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_WS_BASE_URL: string;
  readonly VITE_APP_VERSION: string;
  readonly VITE_APP_NAME: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
} 