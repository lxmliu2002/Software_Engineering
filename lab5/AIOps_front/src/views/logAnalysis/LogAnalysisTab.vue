<template>
    <div class="mainContainer">
        <!-- 面包屑导航 -->
        <el-breadcrumb separator-class="el-icon-arrow-right">
                <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
                <el-breadcrumb-item>日志检测</el-breadcrumb-item>
        </el-breadcrumb>
        <!-- 卡片视图区域 -->
        <el-card class="cardContainer">
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
                        <el-button type="primary" @click="handleExport(logData)">
                            <el-icon class="iconfont icon-daochubiaoge"></el-icon>
                            <span>导出表格</span>
                        </el-button>
                    </el-col>
            </el-row>
            <!-- 日志列表区域  -->
            <el-table height='3.2rem' @sort-change="sortChange" :data="logData.slice((pageparm.currentPage - 1) * pageparm.pageSize, pageparm.currentPage * pageparm.pageSize)"  v-loading="loading" border element-loading-text="拼命加载中" stripe style="margin:0.15rem 0rem 0.15rem 0rem;max-height: 3.2rem;">
                    <el-table-column align="left" label="日志内容" prop="log" :show-overflow-tooltip='true' min-width="70"></el-table-column>
                    <el-table-column align="center" label="预测结果" prop="pred" :show-overflow-tooltip='true' min-width="30"></el-table-column>
                    <el-table-column align="left" label="预测解释" prop="desc" :show-overflow-tooltip='true' min-width="110"></el-table-column>
            </el-table>
            <!-- 分页组件 -->
            <PaginateView v-bind:child-msg="pageparm" @callFather="callFather"></PaginateView>
        </el-card>
    </div>
    </template>
    
    <script>
    import tableSortChange from '../../utils/tableSortChange'
    import {formatDate} from '../../utils/timeEffect'
    import {get} from '../../utils/request';
    import PaginateView from '../../components/PaginateView'
    import {post} from '../../utils/request';
    import { ElMessage } from "element-plus";
    export default {
        name:'LogAnalysisTab',
        components:{PaginateView},
        data () {
            return {
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
            }
        },
        created () {
            this.getLogList();
            
        },
        methods: {
            // 模拟的全部用户列表
            async getLogList () {
                try {
                const result = await post('log/detection', {file_name: 'manual_log.txt', model:'gemma2:9b'});
                if (result?.msg === "success") {
                    this.logData = result.data.data;
                    this.logData = this.logData.filter(item => item.desc.length > 10);
                    console.log(this.logData)
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
            // 获取用户列表（包括全部与单个两种情况）
            async getUser(query){
                this.userList = [];
                if(query!=''){
                    // console.log("请求路由：/user/miseruser/info/user000001")
                    try{
                        const result = await get(`miseruser/getUser/${query}`)
                        if (result?.msg === "success" && result?.userInfo) {
                            this.userList.push(result.userInfo) //获取到数据
                            this.loading = false
                            this.pageparm.currentPage = this.formInline.page
                            this.pageparm.pageSize = this.formInline.limit
                            this.pageparm.total =  this.userList.length
                        }else if(result?.msg === "该用户信息不存在"){
                            this.$message.info("该用户信息不存在！");
                        }else{
                            this.$message.error("未获取到数据，请重新输入！");
                        }
                    }catch{
                        this.$message.error("未获取到数据，请重新输入！");
                    }
                }else{
                    try{
                        // console.log("请求路由：/user/miseruser/list")
                        const result = await get('miseruser/getUserlist')
                        if (result?.msg === "success" && result?.userList) {
                            this.userList = result.userList
                            this.loading = false
                            this.pageparm.currentPage = this.formInline.page
                            this.pageparm.pageSize = this.formInline.limit
                            this.pageparm.total =  this.userList.length
                        }else{
                            this.$message.error("未获取到数据，请重新获取！");
                        }
                    }catch{
                        this.$message.error("未获取到数据，请重新获取！");
                    }
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
                console.log(this.formInline)
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
            // 自定义表格排序规则
            sortChange(column){
                console.log(column)
                // 拷贝排序时的列数类型参数
                this.column = column;
                // this.logData = JSON.parse(JSON.stringify(tableSortChange(column,this.logData)));
            },
            // 将后端传递过来的时间进行格式转换
            formatDate(row, column) {
                // 获取单元格数据
                let data = row[column.property]
                return formatDate(data)
            }
        }
    }
    </script>
    
    <style lang="scss" scoped>
    .mainContainer{
        width:100%;
        height: 100%;
        padding:0.15rem;
        .cardContainer{
            margin: 0.15rem 0 0rem 0;
        }
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