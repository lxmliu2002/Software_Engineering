<template>
    <div class="mainContainer">
        <!-- 面包屑导航 -->
        <el-breadcrumb separator-class="el-icon-arrow-right">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>日志分析</el-breadcrumb-item>
        </el-breadcrumb>

        <!-- 上传文件和文本输入 -->
        <el-card class="cardContainer">
            <el-upload ref="upload" class="upload-demo" :file-list="fileList" :auto-upload="false" @change="handleChange">
                <el-button slot="trigger" type="primary">选取文件</el-button>
            </el-upload>
            <el-button style="margin-top: 10px; margin-bottom: 10px" type="success" @click="submitUpload">上传并分析日志</el-button>
            <el-input type="textarea"
                      :rows="10"
                      placeholder="在这里输入日志内容"
                      v-model="manualLogInput"></el-input>
            <el-button type="primary" @click="analyzeManualLog">分析文本日志</el-button>
        </el-card>

        <el-card class="cardContainer" v-if="hasResult">
            <!-- 按钮区域 -->
            <el-row :gutter="20">
                    <el-col :span="7">
                        <!-- 搜索、导出、添加区域 -->
                        <el-input placeholder="请输入异常情况（默认筛选全部）" style="position:relative" clearable @clear="showAll" v-model="query">
                            <template #append>
                                <el-button type="primary" class="iconfont icon-sousuo" @click="filterLog"></el-button>
                            </template>
                        </el-input>
                    </el-col>
                    <el-col :span="3.5">
                        <el-button type="primary" @click="handleExport(logdata)">
                            <el-icon class="iconfont icon-daochubiaoge"></el-icon>
                            <span>导出表格</span>
                        </el-button>
                    </el-col>
            </el-row>
            <!-- 日志列表区域  -->
            <el-table height='3.2rem' :data="logData.slice((pageparm.currentPage - 1) * pageparm.pageSize, pageparm.currentPage * pageparm.pageSize)"  v-loading="loading" border element-loading-text="拼命加载中" stripe style="margin:0.15rem 0rem 0.15rem 0rem;max-height: 3.2rem;">
                    <el-table-column align="left" label="日志内容" prop="log" :show-overflow-tooltip='true' min-width="70"></el-table-column>
                    <el-table-column align="center" label="预测结果" prop="pred" :show-overflow-tooltip='true' min-width="30"></el-table-column>
                    <el-table-column align="left" label="预测解释" prop="desc" :show-overflow-tooltip='true' min-width="110"></el-table-column>
            </el-table>
            <!-- 分页组件 -->
            <PaginateView v-bind:child-msg="pageparm" @callFather="callFather"></PaginateView>
        </el-card>

        <!-- 日志分析结果展示 -->
        <el-card class="cardContainer" v-if="logData.length">
            <div ref="lineChart" style="width: 100%; height: 400px;"></div>
        </el-card>
        <el-card class="cardContainer" v-if="logData.length">
            <div ref="barChart" style="width: 100%; height: 400px;"></div>
        </el-card>
        <el-card class="cardContainer" v-if="logData.length">
            <div ref="pieChart" style="width: 100%; height: 400px;"></div>
        </el-card>
        <el-card class="cardContainer" v-if="logData.length">
            <div ref="scatterChart" style="width: 100%; height: 400px;"></div>
        </el-card>
        <el-card class="cardContainer" v-if="logData.length">
            <div ref="wordCloud" style="width: 100%; height: 400px;"></div>
        </el-card>
        <el-card class="cardContainer" v-if="logData.length">
            <div ref="stackedAreaChart" style="width: 100%; height: 400px;"></div>
        </el-card>
        <el-card class="cardContainer" v-if="logData.length">
            <div ref="heatMap" style="width: 100%; height: 400px;"></div>
        </el-card>
        <el-card class="cardContainer" v-if="logData.length">
            <div ref="boxPlot" style="width: 100%; height: 400px;"></div>
        </el-card>
        <el-card class="cardContainer" v-if="logData.length">
            <div ref="radarChart" style="width: 100%; height: 400px;"></div>
        </el-card>
        <el-card class="cardContainer" v-if="logData.length">
            <div ref="sankeyChart" style="width: 100%; height: 400px;"></div>
        </el-card>
        <el-card class="cardContainer" v-if="logData.length">
            <el-table :data="logData" style="width: 100%">
                <el-table-column prop="date" label="日期" width="180"></el-table-column>
                <el-table-column prop="hostname" label="主机名" width="180"></el-table-column>
                <el-table-column prop="service" label="服务"></el-table-column>
                <el-table-column prop="message" label="消息"></el-table-column>
                <el-table-column prop="prediction" label="预测"></el-table-column>
                <el-table-column prop="description" label="描述"></el-table-column>
            </el-table>
        </el-card>
    </div>
</template>

<script>
    import axios from 'axios';
    import * as echarts from 'echarts';
    import tableSortChange from '../../utils/tableSortChange'
    import {formatDate} from '../../utils/timeEffect'
    import {get} from '../../utils/request';
    import PaginateView from '../../components/PaginateView'
    import {post} from '../../utils/request';
    import { ElMessage } from "element-plus";

    export default {
        name: 'LogAnalysis',
        components:{PaginateView},
        data() {
            return {
                hasResult: false,
                logData: [],
                fileList: [],
                manualLogInput: '',
                //是否显示加载
                loading: false, 
                // 分页的中间变量
                formInline: {
                    page: 1,
                    limit: 10,
                },
                // 查询参数
                query:'',
                // 分页参数
                pageparm: {
                    currentPage: 1,
                    pageSize: 10,
                    total: 0
                },
                // 排序时的列数类型参数
                column:'',
                // 页面此时需要展示的用户列表
                userList: [],
                // 编辑/增加操作需要的参数
                title: '添加',
                editFormVisible: false, //控制编辑/增加页面显示与隐藏
                editForm: { 
                    userId:'',
                    userName:'',
                    userPassword:'',
                    userPower:'',
                    createTime:''
                },
                // 编辑/增加操作时的rules表单验证
                rules: {
                    userName:[{ required: true, message: '请输入用户名称', trigger: 'blur' }],
                    userPassword:[{ required: true, message: '请输入用户密码', trigger: 'blur' }],
                    userPower: [{ required: true, message: '请输入用户权限', trigger: 'blur' },{ type:'number',message:'必须是数字',trigger: 'blur' }]
                },
                logData: [],
                totalLogData: []
            };
        },
        created () {
            this.getLogList();
            
        },
        methods: {
            handleChange(file, fileList) {
                this.fileList = fileList;
            },
            submitUpload() {
                if (this.fileList.length === 0) {
                    this.$message.error('请先选择一个文件!');
                    return;
                }

                const formData = new FormData();
                formData.append('file', this.fileList[0].raw, this.fileList[0].name);
                const reader = new FileReader();
                reader.onload = (e) => {
                    this.manualLogInput = e.target.result;
                };
                reader.readAsText(this.fileList[0].raw);
                console.log(this.manualLogInput);
                axios.post('http://localhost:8000/file/upload', formData)
                    .then(response => {
                        if (response.data.code === 0) {
                            this.analyzeUploadedLog(this.fileList[0].name);
                        } else {
                            this.$message.error('日志上传失败!');
                        }
                    })
                    .catch(error => {
                        this.$message.error('日志上传失败!');
                    });
                    setTimeout(() => {
                        this.hasResult = true;
                    }, 3000);
                    
            },
            analyzeUploadedLog(fileName) {
                const data = {
                    file_name: fileName,
                    model: 'gemma2:9b'
                };

                axios.post('http://localhost:8000/log/detection', data)
                    .then(response => {
                        if (response.data.code === 0) {
                            this.logData = this.parseLogData(response.data.data);
                            //this.renderCharts();
                        } else {
                            this.$message.error('日志分析失败!');
                        }
                    })
                    .catch(error => {
                        this.$message.error('日志分析失败!');
                    });
            },
            analyzeManualLog() {
                if (!this.manualLogInput) {
                    this.$message.error('请输入要分析的日志内容!');
                    return;
                }
                const data = {
                    file_name: 'manual_log.txt',
                    model: 'gemma2:9b',
                    log: this.manualLogInput
                };

                axios.post('http://localhost:8000/log/detection', data)
                    .then(response => {
                        if (response.data.code === 0) {
                            this.logData = this.parseLogData(response.data.data);
                            this.renderCharts();
                        } else {
                            this.$message.error('文本日志分析失败!');
                        }
                    })
                    .catch(error => {
                        this.$message.error('文本日志分析失败!');
                    });
            },
            parseLogData(logEntries) {
                return logEntries.map(entry => ({
                    date: entry.log.split(' ')[0] + ' ' + entry.log.split(' ')[1],
                    hostname: entry.log.split(' ')[2],
                    service: entry.log.split(' ')[3],
                    message: entry.log.split(' ').slice(4).join(' '),
                    prediction: entry.pred,
                    description: entry.desc
                }));
            },
            /// 模拟的全部日志
            async getLogList () {
                try {
                    const result = await post('log/detection', {file_name: 'manual_log.txt', model:'gemma2:9b'});
                    if (result?.msg === "success") {
                        this.logData = result.data.data;
                        this.logData = this.logData.filter(item => item.desc.length > 10);
                        // console.log(this.logData)
                        this.totalLogData = this.logData;
                        this.loading = false
                        this.pageparm.currentPage = this.formInline.page
                        this.pageparm.pageSize = this.formInline.limit
                        this.pageparm.total =  this.logData.length
                    }
                }catch{
                    ElMessage.error("未获取到数据，请重新获取！")
                }
            },
            // 展示全部数据
            showAll(){
                this.logData = this.totalLogData;
            },
            // 展示查询数据
            filterLog(e){
                if(this.query != '')
                    this.logData = this.totalLogData.filter(item => {
                        return item.pred == this.query
                    });
                else
                    this.logData = this.totalLogData;
            },
            // 分页插件事件--通过改变分页中间变量来改变分页参数
            callFather(parm) {
                this.formInline.page = parm.currentPage
                this.formInline.limit = parm.pageSize
                this.pageparm.currentPage = this.formInline.page
                this.pageparm.pageSize = this.formInline.limit
                //console.log(this.formInline)
                // this.getUserList()
                //this.sortChange(this.column)
            },
            // 导出为表格函数 
            handleExport(logData){
                import('@/utils/exportExcel').then(excel => {
                    const res = [];
                    // excel表示导入的模块对象
                    for(let i =0;i<logData.length;i++){
                        res.push(logData[i])
                    }
                    // const one = res[0] // 返回的数组取第一项
                    // const header = Object.keys(one) // 拿对象中的所有的键
                    const header = ['日志内容','预测结果','预测解释']
                    const data = res.map(item => Object.values(item)) //拿到里面的每一个值
                    excel.export_json_to_excel({
                        header, // 表头 必填
                        data, // 具体数据 必填
                        filename: 'logData', // 文件名称
                        autoWidth: true, // 宽度是否自适应
                        bookType: 'xlsx' // 生成的文件类型
                    })
                })
            },
            // 将后端传递过来的时间进行格式转换
            formatDate(row, column) {
                // 获取单元格数据
                let data = row[column.property]
                return formatDate(data)
            },
            renderCharts() {
                this.renderLineChart();
                this.renderBarChart();
                this.renderPieChart();
                this.renderScatterChart();
                this.renderWordCloud();
                this.renderStackedAreaChart();
                this.renderHeatMap();
                this.renderBoxPlot();
                this.renderRadarChart();
                this.renderSankeyChart();
            },
            renderLineChart() {
                const chartDom = this.$refs.lineChart;
                const myChart = echarts.init(chartDom);
                const dates = this.logData.map(entry => entry.date);
                const services = [...new Set(this.logData.map(entry => entry.service))];
                const seriesData = services.map(service => ({
                    name: service,
                    type: 'line',
                    data: this.logData.filter(entry => entry.service === service).map(entry => entry.message.length)
                }));

                const option = {
                    title: {
                        text: '日志数量随时间变化'
                    },
                    tooltip: {
                        trigger: 'axis'
                    },
                    legend: {
                        data: services
                    },
                    xAxis: {
                        type: 'category',
                        data: dates
                    },
                    yAxis: {
                        type: 'value'
                    },
                    series: seriesData
                };

                myChart.setOption(option);
            },
            renderBarChart() {
                const chartDom = this.$refs.barChart;
                const myChart = echarts.init(chartDom);
                const services = [...new Set(this.logData.map(entry => entry.service))];
                const serviceCount = this.logData.reduce((acc, entry) => {
                    acc[entry.service] = (acc[entry.service] || 0) + 1;
                    return acc;
                }, {});
                const seriesData = Object.entries(serviceCount).map(([service, count]) => ({
                    name: service,
                    value: count
                }));

                const option = {
                    title: {
                        text: '不同服务的日志数量'
                    },
                    tooltip: {
                        trigger: 'axis'
                    },
                    xAxis: {
                        type: 'category',
                        data: services
                    },
                    yAxis: {
                        type: 'value'
                    },
                    series: [{
                        data: seriesData.map(item => item.value),
                        type: 'bar'
                    }]
                };

                myChart.setOption(option);
            },
            renderPieChart() {
                const chartDom = this.$refs.pieChart;
                const myChart = echarts.init(chartDom);
                const serviceCount = this.logData.reduce((acc, entry) => {
                    acc[entry.service] = (acc[entry.service] || 0) + 1;
                    return acc;
                }, {});
                const seriesData = Object.entries(serviceCount).map(([service, count]) => ({
                    name: service,
                    value: count
                }));

                const option = {
                    title: {
                        text: '不同服务的日志分布',
                        left: 'center'
                    },
                    tooltip: {
                        trigger: 'item'
                    },
                    legend: {
                        orient: 'vertical',
                        left: 'left',
                        data: Object.keys(serviceCount)
                    },
                    series: [
                        {
                            name: '服务',
                            type: 'pie',
                            radius: '50%',
                            data: seriesData,
                            emphasis: {
                                itemStyle: {
                                    shadowBlur: 10,
                                    shadowOffsetX: 0,
                                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                                }
                            }
                        }
                    ]
                };

                myChart.setOption(option);
            },
            renderScatterChart() {
                const chartDom = this.$refs.scatterChart;
                const myChart = echarts.init(chartDom);
                const seriesData = this.logData.map(entry => ({
                    name: entry.service,
                    value: [entry.date, entry.message.length]
                }));

                const option = {
                    title: {
                        text: '日志消息长度散点图'
                    },
                    tooltip: {
                        trigger: 'item'
                    },
                    xAxis: {
                        type: 'category',
                        data: this.logData.map(entry => entry.date)
                    },
                    yAxis: {
                        type: 'value'
                    },
                    series: [{
                        name: '消息长度',
                        type: 'scatter',
                        data: seriesData.map(item => item.value)
                    }]
                };

                myChart.setOption(option);
            },
            renderWordCloud() {
                const chartDom = this.$refs.wordCloud;
                const myChart = echarts.init(chartDom);
                const wordFrequency = this.logData.reduce((acc, entry) => {
                    const words = entry.message.split(' ');
                    words.forEach(word => {
                        acc[word] = (acc[word] || 0) + 1;
                    });
                    return acc;
                }, {});
                const seriesData = Object.entries(wordFrequency).map(([word, count]) => ({
                    name: word,
                    value: count
                }));

                const option = {
                    title: {
                        text: '日志消息词云图'
                    },
                    tooltip: {
                        trigger: 'item'
                    },
                    series: [{
                        type: 'wordCloud',
                        data: seriesData
                    }]
                };

                myChart.setOption(option);
            },
            renderStackedAreaChart() {
                const chartDom = this.$refs.stackedAreaChart;
                const myChart = echarts.init(chartDom);
                const dates = this.logData.map(entry => entry.date);
                const services = [...new Set(this.logData.map(entry => entry.service))];
                const seriesData = services.map(service => ({
                    name: service,
                    type: 'line',
                    stack: '总量',
                    areaStyle: {},
                    data: this.logData.filter(entry => entry.service === service).map(entry => entry.message.length)
                }));

                const option = {
                    title: {
                        text: '堆叠面积图'
                    },
                    tooltip: {
                        trigger: 'axis'
                    },
                    legend: {
                        data: services
                    },
                    xAxis: {
                        type: 'category',
                        boundaryGap: false,
                        data: dates
                    },
                    yAxis: {
                        type: 'value'
                    },
                    series: seriesData
                };

                myChart.setOption(option);
            },
            renderHeatMap() {
                const chartDom = this.$refs.heatMap;
                const myChart = echarts.init(chartDom);
                const dates = [...new Set(this.logData.map(entry => entry.date))];
                const services = [...new Set(this.logData.map(entry => entry.service))];
                const data = this.logData.map(entry => [dates.indexOf(entry.date), services.indexOf(entry.service), entry.message.length]);

                const option = {
                    title: {
                        text: '热力图'
                    },
                    tooltip: {
                        position: 'top'
                    },
                    grid: {
                        height: '50%',
                        top: '10%'
                    },
                    xAxis: {
                        type: 'category',
                        data: dates,
                        splitArea: {
                            show: true
                        }
                    },
                    yAxis: {
                        type: 'category',
                        data: services,
                        splitArea: {
                            show: true
                        }
                    },
                    visualMap: {
                        min: 0,
                        max: Math.max(...data.map(d => d[2])),
                        calculable: true,
                        orient: 'horizontal',
                        left: 'center',
                        bottom: '15%'
                    },
                    series: [{
                        name: '服务日志数量',
                        type: 'heatmap',
                        data: data,
                        label: {
                            show: true
                        },
                        emphasis: {
                            itemStyle: {
                                shadowBlur: 10,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                        }
                    }]
                };

                myChart.setOption(option);
            },
            renderBoxPlot() {
                const chartDom = this.$refs.boxPlot;
                const myChart = echarts.init(chartDom);
                const data = this.logData.map(entry => entry.message.length);

                const option = {
                    title: {
                        text: '箱线图'
                    },
                    tooltip: {
                        trigger: 'item',
                        axisPointer: {
                            type: 'shadow'
                        }
                    },
                    grid: {
                        left: '10%',
                        right: '10%',
                        bottom: '15%'
                    },
                    xAxis: {
                        type: 'category',
                        data: ['日志消息长度'],
                        boundaryGap: true,
                        splitArea: {
                            show: false
                        },
                        axisLabel: {
                            formatter: '长度'
                        }
                    },
                    yAxis: {
                        type: 'value',
                        splitArea: {
                            show: true
                        }
                    },
                    series: [{
                        name: 'boxplot',
                        type: 'boxplot',
                        data: [[
                            Math.min(...data),
                            Math.max(...data)
                        ]],
                        tooltip: {
                            formatter: function (param) {
                                return [
                                    '日志消息长度: ',
                                    '最大值: ' + param.data[1],
                                    '最小值: ' + param.data[0]
                                ].join('<br/>');
                            }
                        }
                    }]
                };

                myChart.setOption(option);
            },
            renderRadarChart() {
                const chartDom = this.$refs.radarChart;
                const myChart = echarts.init(chartDom);
                const services = [...new Set(this.logData.map(entry => entry.service))];
                const data = services.map(service => this.logData.filter(entry => entry.service === service).map(entry => entry.message.length).reduce((a, b) => a + b, 0));

                const option = {
                    title: {
                        text: '雷达图'
                    },
                    tooltip: {},
                    legend: {
                        data: ['服务']
                    },
                    radar: {
                        indicator: services.map(service => ({ name: service, max: Math.max(...data) }))
                    },
                    series: [{
                        name: '服务',
                        type: 'radar',
                        data: [{
                            value: data,
                            name: '服务'
                        }]
                    }]
                };

                myChart.setOption(option);
            },
            renderSankeyChart() {
                const chartDom = this.$refs.sankeyChart;
                const myChart = echarts.init(chartDom);
                const services = [...new Set(this.logData.map(entry => entry.service))];
                const nodes = services.map(service => ({ name: service }));
                const links = this.logData.map(entry => ({
                    source: entry.hostname,
                    target: entry.service,
                    value: entry.message.length
                }));

                const option = {
                    title: {
                        text: '桑基图'
                    },
                    tooltip: {
                        trigger: 'item',
                        triggerOn: 'mousemove'
                    },
                    series: [{
                        type: 'sankey',
                        layout: 'none',
                        data: nodes,
                        links: links,
                        emphasis: {
                            focus: 'adjacency'
                        },
                        lineStyle: {
                            color: 'gradient',
                            curveness: 0.5
                        }
                    }]
                };

                myChart.setOption(option);
            }
        }
    };
</script>

<style scoped>
    .mainContainer{
        width:100%;
        height: 100%;
        padding:0.15rem;
        .cardContainer{
            margin: 0.15rem 0 0rem 0;
        }
    }

    .cardContainer {
        margin-top: 20px;
    }
    


    .icon-sousuo{
        width:100%;
        height: 100%;
        position: absolute;
        margin:0 auto;
    }
    .icon-sousuo:hover::before{
        color:#409eff;
    }
    .iconfont{
        margin-right: 0;
    }
    .icon-tianjiayonghu,.icon-daochubiaoge,.icon-shanchupiliangshanchu{
        color:#fff !important;
    }
</style>
