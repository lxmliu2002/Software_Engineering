<template>
  <div class="visualization">
    <div class="header">
      <h1>可视化大屏</h1>
      <div class="update-time">{{ currentTime }}</div>
    </div>
    <div class="content">
      <div class="column left">
        <div class="chart-container">
          <div
            class="chart"
            ref="chart1"
            style="height: 300px; width: 100%"
          ></div>
          <div class="controls">
            <button @click="showAverage">计算均值</button>
            <button @click="showMax">计算峰值</button>
            <div v-if="average">
              代码提交频率平均值: {{ codeSubmitStats.avg }}, Bug修复速度平均值:
              {{ bugFixStats.avg }}
            </div>
            <div v-if="max">
              代码提交频率峰值: {{ codeSubmitStats.max }}, Bug修复速度峰值:
              {{ bugFixStats.max }}
            </div>
          </div>
        </div>
        <div class="chart api-chart">
          <h2 class="table-title">磁盘预测的数据状态</h2>
          <div
            v-if="apiData && apiData.length"
            class="api-data-table-container"
          >
            <table class="api-data-table">
              <thead>
                <tr>
                  <th>序列号</th>
                  <th>日期</th>
                  <th>预测天数</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in apiData" :key="item.serial_number">
                  <td>{{ item.serial_number }}</td>
                  <td>{{ formatDate(item.date) }}</td>
                  <td>{{ item.predicted_days_to_failure }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <div class="column center">
        <div class="chart-container">
          <div
            class="chart"
            ref="gaugeChart"
            style="height: 300px; width: 100%"
          ></div>
        </div>
        <div
          class="chart"
          ref="chart4"
          style="height: 300px; width: 100%"
        ></div>
      </div>
      <div class="column right">
        <div class="chart-container right-upper">
          <div class="chart-subcontainer upper-half">
            <div
              class="chart-half"
              ref="radarChart"
              style="height: 100%; width: 100%"
            ></div>
            <div
              class="chart-half"
              ref="distributionChart"
              style="height: 100%; width: 100%"
            ></div>
          </div>
          <div
            class="chart lower-half"
            ref="barChart"
            style="height: 100%; width: 100%"
          ></div>
        </div>
        <div
          class="chart right-lower"
          ref="chart6"
          style="height: 300px; width: 100%"
        ></div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { get, post } from '@/utils/request.js' // 引入封装的get和post请求方法

export default {
  name: 'Visualization',
  data() {
    return {
      currentTime: this.getCurrentTime(),
      average: false,
      max: false,
      codeSubmitStats: { avg: 0, max: 0 },
      bugFixStats: { avg: 0, max: 0 },
      repoSize: 1500, // 代码库大小
      activeTasks: 30, // 活跃的维护任务数量
      recentLogs: [
        '2024-07-04 16:00:00 - 提交更新代码',
        '2024-07-04 15:45:00 - 修复了一个Bug',
        '2024-07-04 15:30:00 - 完成了新的功能模块',
        '2024-07-04 15:15:00 - 代码重构',
        '2024-07-04 15:00:00 - 修复了一个bug',
        '2024-07-04 14:45:00 - 提交更新代码',
        // 添加更多日志
      ],
      chart6Data: [
        { label: '代码质量', value: 90 },
        { label: '任务完成率', value: 85 },
        { label: '日志覆盖率', value: 80 },
        { label: '测试通过率', value: 88 },
        // { label: '用户满意度', value: 92 },
      ],
      apiData: [], // 存储API返回的数据
    }
  },
  mounted() {
    this.$nextTick(() => {
      setTimeout(() => {
        this.initCharts()
        this.startTimer()
        this.fetchData() // 在组件加载时调用API
        this.initPieChart() // 初始化饼图
      }, 500) // 延迟500毫秒
    })
  },

  beforeDestroy() {
    clearInterval(this.timer)
  },
  methods: {
    getCurrentTime() {
      const now = new Date()
      const year = now.getFullYear()
      const month = String(now.getMonth() + 1).padStart(2, '0')
      const date = String(now.getDate()).padStart(2, '0')
      const hours = String(now.getHours()).padStart(2, '0')
      const minutes = String(now.getMinutes()).padStart(2, '0')
      const seconds = String(now.getSeconds()).padStart(2, '0')
      return `${year}-${month}-${date} ${hours}:${minutes}:${seconds}`
    },
    startTimer() {
      this.timer = setInterval(() => {
        this.currentTime = this.getCurrentTime()
      }, 1000)
    },
    async fetchData() {
      try {
        // 调用第一个API来训练模型
        const trainResponse = await post('/disk/train/daysAfter', {
          file_name: 'days.csv',
        })
        const modelName = trainResponse.data.model_name

        // 使用获取到的模型名称调用第二个API来进行预测
        const predictResponse = await post('/disk/predict/daysAfter', {
          file_name: 'test_day.csv',
          model_name: modelName,
        })
        this.apiData = JSON.parse(predictResponse.data) // 将字符串解析为JSON对象

        // 调试信息
        console.log('API Data:', this.apiData)
        console.log('API Data Type:', typeof this.apiData)
        console.log('Is Array:', Array.isArray(this.apiData))

        // 确保 this.apiData 是一个数组
        if (!Array.isArray(this.apiData)) {
          console.error('API Data is not an array:', this.apiData)
          return
        }

        // 在 nextTick 中初始化 API 数据表格
        this.$nextTick(() => {
          this.initApiChart()
        })
      } catch (error) {
        console.error('API Error:', error)
      }
    },
    initCharts() {
      this.$nextTick(() => {
        const chart1 = echarts.init(this.$refs.chart1)
        this.gaugeChart = echarts.init(this.$refs.gaugeChart)
        this.chart4 = echarts.init(this.$refs.chart4)
        this.radarChart = echarts.init(this.$refs.radarChart)
        this.distributionChart = echarts.init(this.$refs.distributionChart)
        this.barChart = echarts.init(this.$refs.barChart)

        const option1 = {
          title: {
            text: '代码运维状态',
            left: 'center',
            textStyle: {
              color: '#fff',
            },
          },
          tooltip: {
            trigger: 'axis',
          },
          xAxis: {
            type: 'category',
            boundaryGap: false,
            data: ['A', 'B', 'C', 'D', 'E', 'F'],
            axisLine: {
              lineStyle: {
                color: '#fff',
              },
            },
          },
          yAxis: {
            type: 'value',
            axisLine: {
              lineStyle: {
                color: '#fff',
              },
            },
          },
          series: [
            {
              name: '代码提交频率',
              type: 'line',
              stack: '总量',
              smooth: true, // 将折线改为平滑的曲线
              data: [20, 32, 41, 34, 40, 30],
              itemStyle: {
                color: '#1E90FF',
              },
              areaStyle: {
                // 填充颜色
                color: 'rgba(30, 144, 255, 0.5)',
              },
            },
            {
              name: 'Bug修复速度',
              type: 'line',
              stack: '总量',
              smooth: true, // 将折线改为平滑的曲线
              data: [25, 42, 31, 54, 40, 50],
              itemStyle: {
                color: '#32cd32',
              },
              areaStyle: {
                // 填充颜色
                color: 'rgba(50, 205, 50, 0.5)',
              },
            },
          ],
        }

        chart1.setOption(option1)
        this.updateCharts()
        this.initRadarChart()
        this.initDistributionChart()
        this.initStackedBarChart()

        const codeSubmitData = [20, 32, 41, 34, 40, 30]
        const bugFixData = [25, 42, 31, 54, 40, 50]

        this.codeSubmitStats = this.calculateStatistics(codeSubmitData)
        this.bugFixStats = this.calculateStatistics(bugFixData)
      })
    },
    initRadarChart() {
      this.$nextTick(() => {
        const radarOption = {
          title: {
            text: '',
          },
          tooltip: {},
          radar: {
            indicator: [
              { name: '语言', max: 100 },
              { name: '操作系统', max: 100 },
              { name: '数据库', max: 100 },
              { name: '工具', max: 100 },
              { name: '框架', max: 100 },
              { name: '其他', max: 100 },
            ],
            shape: 'circle',
            splitNumber: 5,
            axisLine: {
              lineStyle: {
                color: 'rgba(255, 255, 255, 0.5)',
              },
            },
            splitLine: {
              lineStyle: {
                color: 'rgba(255, 255, 255, 0.5)',
              },
            },
            splitArea: {
              areaStyle: {
                color: 'rgba(255, 255, 255, 0.1)',
              },
            },
          },
          series: [
            {
              name: '数据分布',
              type: 'radar',
              data: [
                {
                  value: [80, 90, 70, 60, 80, 70],
                  name: '数据分布',
                  areaStyle: {
                    color: 'rgba(255, 255, 255, 0.5)',
                  },
                },
              ],
            },
          ],
        }
        this.radarChart.setOption(radarOption)
      })
    },
    initDistributionChart() {
      this.$nextTick(() => {
        const distributionOption = {
          title: {
            text: '',
          },
          tooltip: {},
          series: [
            {
              name: '检测类型',
              type: 'pie',
              radius: '55%',
              data: [
                { value: 35, name: '语言' },
                { value: 25, name: '操作系统' },
                { value: 20, name: '数据库' },
                { value: 10, name: '工具' },
                { value: 5, name: '框架' },
                { value: 5, name: '其他' },
              ],
              emphasis: {
                itemStyle: {
                  shadowBlur: 10,
                  shadowOffsetX: 0,
                  shadowColor: 'rgba(0, 0, 0, 0.5)',
                },
              },
            },
          ],
        }
        this.distributionChart.setOption(distributionOption)
      })
    },
    initStackedBarChart() {
      this.$nextTick(() => {
        const stackedBarOption = {
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow',
            },
          },
          legend: {
            data: ['直接访问', '邮件营销', '联盟广告', '视频广告', '搜索引擎'],
            textStyle: {
              color: '#fff',
            },
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true,
          },
          xAxis: {
            type: 'value',
            axisLine: {
              lineStyle: {
                color: '#fff',
              },
            },
          },
          yAxis: {
            type: 'category',
            data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
            axisLine: {
              lineStyle: {
                color: '#fff',
              },
            },
          },
          series: [
            {
              name: '直接访问',
              type: 'bar',
              stack: '总量',
              label: {
                show: true,
                position: 'insideRight',
              },
              data: [320, 302, 301, 334, 390, 330, 320],
              itemStyle: {
                color: '#1E90FF',
              },
            },
            {
              name: '邮件营销',
              type: 'bar',
              stack: '总量',
              label: {
                show: true,
                position: 'insideRight',
              },
              data: [120, 132, 101, 134, 90, 230, 210],
              itemStyle: {
                color: '#32cd32',
              },
            },
            {
              name: '联盟广告',
              type: 'bar',
              stack: '总量',
              label: {
                show: true,
                position: 'insideRight',
              },
              data: [220, 182, 191, 234, 290, 330, 310],
              itemStyle: {
                color: '#FF4500',
              },
            },
            {
              name: '视频广告',
              type: 'bar',
              stack: '总量',
              label: {
                show: true,
                position: 'insideRight',
              },
              data: [150, 212, 201, 154, 190, 330, 410],
              itemStyle: {
                color: '#FFD700',
              },
            },
            {
              name: '搜索引擎',
              type: 'bar',
              stack: '总量',
              label: {
                show: true,
                position: 'insideRight',
              },
              data: [820, 732, 701, 734, 1090, 1130, 1120],
              itemStyle: {
                color: '#8A2BE2',
              },
            },
          ],
        }
        this.barChart.setOption(stackedBarOption)
      })
    },
    updateCharts() {
      this.$nextTick(() => {
        const gaugeOption = {
          tooltip: {
            formatter: '{a} <br/>{b} : {c}%',
          },
          toolbox: {
            feature: {
              restore: {},
              saveAsImage: {},
            },
          },
          series: [
            {
              name: '系统健康',
              type: 'gauge',
              detail: { formatter: '{value}%' },
              data: [{ value: this.calculateHealthScore(), name: '健康度' }],
              axisLine: {
                lineStyle: {
                  width: 30,
                  color: [
                    [0.3, '#ff4500'],
                    [0.7, '#48b'],
                    [1, '#228b22'],
                  ],
                },
              },
              splitLine: {
                length: 30,
                lineStyle: {
                  color: 'auto',
                },
              },
              pointer: {
                width: 5,
              },
            },
          ],
        }

        const barOption = {
          title: {
            text: '系统总体健康状态',
            left: 'center',
            textStyle: {
              color: '#fff',
            },
          },
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow',
            },
          },
          xAxis: {
            type: 'category',
            data: ['代码库大小', '活跃任务', '日志条目'],
            axisLine: {
              lineStyle: {
                color: '#fff',
              },
            },
          },
          yAxis: {
            type: 'value',
            axisLine: {
              lineStyle: {
                color: '#fff',
              },
            },
          },
          series: [
            {
              name: '数量',
              type: 'bar',
              data: [this.repoSize, this.activeTasks, this.recentLogs.length],
              itemStyle: {
                color: '#32cd32',
              },
            },
          ],
        }

        this.gaugeChart.setOption(gaugeOption)
        this.chart4.setOption(barOption)
      })
    },
    calculateStatistics(data) {
      const sum = data.reduce((acc, val) => acc + val, 0)
      const avg = sum / data.length
      const max = Math.max(...data)
      return { avg, max }
    },
    showAverage() {
      this.average = true
      this.max = false
    },
    showMax() {
      this.average = false
      this.max = true
    },
    calculateHealthScore() {
      // 一个简单的健康评分计算方法，可以根据实际需求进行调整
      const logImpact = Math.min(this.recentLogs.length * 10, 100)
      const taskImpact = Math.min(this.activeTasks * 2, 100)
      const baseHealth = 100 - (logImpact + taskImpact) / 2
      return Math.max(baseHealth, 0)
    },
    getGradient(value) {
      if (value >= 90) return 'linear-gradient(to top, #00c6ff, #0072ff)'
      if (value >= 80) return 'linear-gradient(to top, #00c6ff, #0072ff)'
      if (value >= 70) return 'linear-gradient(to top, #00c6ff, #0072ff)'
      return 'linear-gradient(to top, #ff7e5f, #feb47b)'
    },
    formatDate(timestamp) {
      const date = new Date(timestamp)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    },
    initApiChart() {
      this.$nextTick(() => {
        // 检查 this.$refs.apiChart 是否存在
        if (!this.$refs.apiChart) {
          console.error('Cannot find apiChart element')
          return
        }

        // 检查 this.apiData 是否有值且为数组
        if (
          !this.apiData ||
          !Array.isArray(this.apiData) ||
          this.apiData.length === 0
        ) {
          console.error(
            'API Data is empty, not an array, or not available:',
            this.apiData
          )
          return
        }

        const apiChart = echarts.init(this.$refs.apiChart)

        const option = {
          title: {
            text: '预测的用户数据状态',
            left: 'center',
            textStyle: {
              color: '#fff',
            },
          },
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow',
            },
          },
          xAxis: {
            type: 'category',
            data: this.apiData.map((item) => item.serial_number),
            axisLine: {
              lineStyle: {
                color: '#fff',
              },
            },
          },
          yAxis: {
            type: 'value',
            axisLine: {
              lineStyle: {
                color: '#fff',
              },
            },
          },
          series: [
            {
              name: '预测天数',
              type: 'bar',
              data: this.apiData.map((item) => item.predicted_days_to_failure),
              itemStyle: {
                color: '#32cd32',
              },
            },
          ],
        }

        apiChart.setOption(option)
      })
    },
    // 新增方法来初始化饼图
    initPieChart() {
      this.$nextTick(() => {
        const data = [
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 1, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 1],
          ['ST12000NM0007', 0, 1],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 1, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 1],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 1],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 1, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 0],
          ['ST12000NM0007', 1, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 1, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 1],
          ['ST12000NM0007', 1, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 1, 1],
          ['ST12000NM0007', 0, 0],
          ['ST12000NM0007', 0, 0],
        ]

        let correct = 0
        let incorrect = 0

        data.forEach((item) => {
          if (item[1] === item[2]) {
            correct++
          } else {
            incorrect++
          }
        })

        const pieChart = echarts.init(this.$refs.chart6)
        const pieOption = {
          title: {
            text: '磁盘预测结果统计',
            left: 'center',
            textStyle: {
              color: '#fff',
            },
          },
          tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b} : {c} ({d}%)',
          },
          series: [
            {
              name: '预测结果',
              type: 'pie',
              radius: '55%',
              data: [
                { value: correct, name: '预测正确' },
                { value: incorrect, name: '预测错误' },
              ],
              emphasis: {
                itemStyle: {
                  shadowBlur: 10,
                  shadowOffsetX: 0,
                  shadowColor: 'rgba(0, 0, 0, 0.5)',
                },
              },
            },
          ],
        }

        pieChart.setOption(pieOption)
      })
    },
  },
}
</script>

<style scoped>
.visualization {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #1f2d3d;
  color: #fff;
}

.header {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  background-color: #334157;
  position: relative;
}

.header h1 {
  margin: 0;
}

.update-time {
  position: absolute;
  right: 20px;
  font-size: 14px;
}

.content {
  display: flex;
  flex: 1;
  padding: 20px;
  justify-content: space-between;
}

.column {
  display: flex;
  flex-direction: column;
  flex: 1;
  justify-content: space-between;
}

.chart-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  margin-bottom: 20px;
}

.chart-subcontainer {
  display: flex;
  flex-direction: row; /* 将方向改为row以便左右布局 */
  height: 50%;
  margin-bottom: 20px;
}

.chart-half {
  flex: 1;
  height: 100%; /* 设置明确的高度 */
  margin-right: 10px;
}

.chart-half:last-child {
  margin-right: 0;
}

.chart {
  background-color: #2b3a4d;
  border-radius: 10px;
  padding: 20px;
  flex: 1;
}

.chart-title {
  text-align: center;
  color: #fff;
}

.info-panel {
  margin-top: 10px;
  padding: 10px;
  background-color: #334157;
  border-radius: 5px;
}

.info-panel p {
  margin: 5px 0;
  color: #fff;
}

.info-panel ul {
  padding-left: 20px;
  color: #fff;
}

.chart table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  color: #fff;
}

.chart th,
.chart td {
  border: 1px solid #fff;
  padding: 8px;
}

.chart th {
  background-color: #334157;
}

.chart tr:nth-child(even) {
  background-color: #2b3a4d;
}

.table-title {
  text-align: center;
  margin-bottom: 10px;
  color: #fff;
}

.controls {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px;
}

.controls button {
  margin: 10px;
  padding: 10px 20px;
  background-color: #334157;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.controls button:hover {
  background-color: #556377;
}

.circle-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: center; /* 中心对齐 */
  align-items: center;
  height: 100%; /* 让容器高度占满父元素 */
  width: 100%; /* 让容器宽度占满父元素 */
}

.circle-item {
  width: 50%; /* 每个圆圈占容器的一半宽度 */
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #fff;
  font-size: 20px;
  background: linear-gradient(to top, #00c6ff, #0072ff);
}

.circle-text {
  font-size: 24px;
}

.circle-label {
  margin-top: 10px;
  font-size: 16px;
  color: #fff;
}

.api-chart {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column; /* 添加这一行以垂直对齐 */
  flex: 1;
}

.api-data-table-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  width: 100%;
}

.api-data-table {
  width: 90%;
  margin: auto;
  border-collapse: collapse;
  text-align: center;
  background-color: #2b3a4d;
  border-radius: 10px;
}

.api-data-table th,
.api-data-table td {
  border: 1px solid #fff;
  padding: 12px;
}

.api-data-table th {
  background-color: #334157;
}

.api-data-table tr:nth-child(even) {
  background-color: #2b3a4d;
}
</style>
