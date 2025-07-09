declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module '@vicons/*' {
  import type { Component } from 'vue'
  const component: Component
  export default component
} 