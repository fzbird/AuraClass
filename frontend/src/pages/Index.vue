<template>
  <div class="home-container">
    <header class="hero-section">
      <div class="overlay"></div>
      <div class="hero-content">
        <h1 class="hero-title">AuraClass 班级量化管理系统</h1>
        <p class="hero-subtitle">提升班级管理效率，激发学生潜能</p>
        
        <div class="hero-buttons-container">
          <n-button type="primary" size="large" @click="goToLogin" class="hero-button">
            登录系统
          </n-button>
          <n-button size="large" @click="scrollToFeatures" class="hero-button secondary">
            了解功能
          </n-button>
        </div>
      </div>
    </header>
    
    <section id="features" class="features-section container mx-auto">
      <div class="section-header text-center">
        <h2>核心功能</h2>
        <p>全面的班级量化管理解决方案</p>
      </div>
      
      <n-grid :cols="3" :x-gap="24" :y-gap="24" responsive="screen" :item-responsive="true">
        <n-grid-item span="3 m:1 l:1" v-for="(feature, index) in features" :key="index">
          <n-card class="feature-card">
            <template #header>
              <div class="feature-icon">
                <n-icon :size="32" :color="feature.color">
                  <component :is="feature.icon" />
                </n-icon>
              </div>
            </template>
            <h3 class="feature-title">{{ feature.title }}</h3>
            <p class="feature-desc">{{ feature.description }}</p>
          </n-card>
        </n-grid-item>
      </n-grid>
    </section>
    
    <section class="cta-section">
      <div class="container mx-auto">
        <div class="cta-content">
          <h2>准备好提升您的班级管理了吗？</h2>
          <p>立即登录体验AuraClass班级量化管理系统，轻松实现班级精细化管理。</p>
          <n-button type="primary" size="large" @click="goToLogin">
            开始使用
          </n-button>
        </div>
      </div>
    </section>
    
    <footer class="footer-section">
      <div class="container mx-auto">
        <div class="footer-content">
          <div class="footer-logo">
            <h2>AuraClass</h2>
            <p>班级量化管理系统</p>
          </div>
          
          <div class="footer-links">
            <h3>快速链接</h3>
            <ul>
              <li><a href="#features">功能介绍</a></li>
              <li><a href="/auth/login">系统登录</a></li>
            </ul>
          </div>
          
          <div class="footer-contact">
            <h3>联系我们</h3>
            <p>电子邮箱: 36178831@qq.com</p>
            <p>电话: 0537-3517815</p>
          </div>
        </div>
        
        <div class="footer-bottom">
          <p>© {{ currentYear }} AuraClass 班级量化管理系统. 保留所有权利.</p>
          <p>版本: 1.0.0</p>
        </div>
      </div>
    </footer>
    
    <div class="system-status">
      <n-tooltip placement="top">
        <template #trigger>
          <div class="status-indicator" :class="{ 'active': systemActive }"></div>
        </template>
        <div>
          系统状态: {{ systemActive ? '正常运行' : '维护中' }}<br>
          最后更新: {{ lastUpdated }}
        </div>
      </n-tooltip>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { 
  NButton, NGrid, NGridItem, NCard, NIcon, NTooltip,
} from 'naive-ui';
import { 
  BookOutline as BookIcon,
  PeopleOutline as PeopleIcon,
  StatsChartOutline as StatsIcon,
  NotificationsOutline as NotifyIcon,
  SettingsOutline as SettingsIcon,
  BulbOutline as BulbIcon,
} from '@vicons/ionicons5';

const router = useRouter();
const systemActive = ref(true);
const lastUpdated = ref(new Date().toLocaleString());
const currentYear = computed(() => new Date().getFullYear());

const features = [
  {
    title: '学生管理',
    description: '高效管理学生信息、成绩、表现等数据，支持批量导入导出。',
    icon: PeopleIcon,
    color: '#3366FF'
  },
  {
    title: '量化记录',
    description: '记录学生日常行为表现，自定义量化项目和评分标准。',
    icon: BookIcon,
    color: '#52C41A'
  },
  {
    title: '数据分析',
    description: '直观的图表展示班级和学生数据，帮助识别趋势和问题。',
    icon: StatsIcon,
    color: '#FA8C16'
  },
  {
    title: '智能通知',
    description: '重要事件自动提醒，确保信息及时传达给相关人员。',
    icon: NotifyIcon,
    color: '#F5222D'
  },
  {
    title: 'AI助手',
    description: '智能分析学生表现，提供个性化教学建议和解决方案。',
    icon: BulbIcon,
    color: '#722ED1'
  },
  {
    title: '系统设置',
    description: '灵活配置系统参数，满足不同学校和班级的管理需求。',
    icon: SettingsIcon,
    color: '#13C2C2'
  }
];

const goToLogin = () => {
  router.push('/auth/login');
};

const scrollToFeatures = () => {
  const featuresSection = document.getElementById('features');
  if (featuresSection) {
    featuresSection.scrollIntoView({ behavior: 'smooth' });
  }
};

onMounted(() => {
  // 模拟系统状态检查
  setInterval(() => {
    systemActive.value = true;
    lastUpdated.value = new Date().toLocaleString();
  }, 60000); // 每分钟更新一次
});
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.hero-section {
  position: relative;
  height: 100vh;
  min-height: 600px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: white;
  background: url('/images/classroom-bg.jpg') center/cover no-repeat;
  background-color: #3366FF; /* Fallback */
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(51, 102, 255, 0.8);
}

.hero-content {
  position: relative;
  z-index: 10;
  padding: 0 20px;
  width: 100%;
  max-width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  line-height: 1.2;
  width: 100%;
  text-align: center;
}

.hero-subtitle {
  font-size: 1.5rem;
  opacity: 0.9;
  margin-bottom: 2rem;
  width: 100%;
  text-align: center;
}

.text-primary {
  color: #ffffff;
}

.hero-button {
  min-width: 150px;
}

.hero-button.secondary {
  background-color: transparent;
  border: 2px solid white;
  color: white;
}

.hero-button.secondary:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.hero-buttons-container {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  justify-content: center;
  width: 100%;
  margin-top: 2rem;
}

.container {
  width: 100%;
  max-width: 1200px;
  padding: 0 20px;
  margin-left: auto;
  margin-right: auto;
}

.features-section {
  padding: 100px 0;
}

.section-header {
  margin-bottom: 60px;
}

.section-header h2 {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 1rem;
}

.section-header p {
  font-size: 1.2rem;
  color: #666;
}

.feature-card {
  height: 100%;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 70px;
  height: 70px;
  margin: 0 auto 20px;
  border-radius: 50%;
  background-color: #f0f5ff;
}

.feature-title {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  text-align: center;
}

.feature-desc {
  color: #666;
  text-align: center;
}

.cta-section {
  background-color: #f0f5ff;
  padding: 80px 0;
  text-align: center;
}

.cta-content {
  max-width: 800px;
  margin: 0 auto;
}

.cta-content h2 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  color: #333;
}

.cta-content p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  color: #666;
}

.footer-section {
  background-color: #333;
  color: white;
  padding: 60px 0 30px;
}

.footer-content {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  margin-bottom: 40px;
}

.footer-logo, .footer-links, .footer-contact {
  margin-bottom: 30px;
}

.footer-logo h2 {
  font-size: 1.8rem;
  margin-bottom: 0.5rem;
}

.footer-links h3, .footer-contact h3 {
  font-size: 1.2rem;
  margin-bottom: 1rem;
  color: #ccc;
}

.footer-links ul {
  list-style: none;
  padding: 0;
}

.footer-links li {
  margin-bottom: 0.5rem;
}

.footer-links a {
  color: white;
  text-decoration: none;
  transition: color 0.3s ease;
}

.footer-links a:hover {
  color: #3366FF;
}

.footer-bottom {
  padding-top: 30px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
}

.system-status {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 100;
}

.status-indicator {
  width: 15px;
  height: 15px;
  border-radius: 50%;
  background-color: #f5222d;
  cursor: pointer;
}

.status-indicator.active {
  background-color: #52c41a;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-subtitle {
    font-size: 1.2rem;
  }
  
  .section-header h2 {
    font-size: 2rem;
  }
  
  .cta-content h2 {
    font-size: 2rem;
  }
  
  .footer-content {
    flex-direction: column;
  }
}
</style> 