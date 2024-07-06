<template>
    <div class="mainContainer">
        <!-- 面包屑导航 -->
        <el-breadcrumb separator-class="el-icon-arrow-right">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>文件上传</el-breadcrumb-item>
        </el-breadcrumb>

        <!-- 上传文件 -->
        <el-card class="cardContainer">
            <el-upload ref="upload" class="upload-demo" :before-upload="beforeUpload" :file-list="fileList"
                :auto-upload="false" name="file" @change="handleChange">
                <el-button slot="trigger" type="primary">选取文件</el-button>
                <el-button style="margin-left: 10px;" type="success" @click="submitUpload">上传到服务器</el-button>
                <div slot="tip" class="el-upload__tip">  只能上传文件，大小不超过500KB</div>
            </el-upload>
        </el-card>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    name: 'FileUpload',
    data() {
        return {
            fileList: [],
            selectedFile: null,
        };
    },
    methods: {
        beforeUpload(file) {
            const isLt500k = file.size / 1024 / 1024 < 0.5;

            if (!isLt500k) {
                this.$message.error('上传文件大小不能超过 500KB!');
            }
            return isLt500k;
        },
        handleChange(file, fileList) {
            this.selectedFile = file.raw;
            this.fileList = fileList;
        },
        handleSuccess(response, file, fileList) {
            if (response.code === 0) {
                this.$message.success('文件上传成功!');
            } else {
                this.$message.error('文件上传失败!');
            }
            this.fileList = fileList;
        },
        handleError(err, file, fileList) {
            this.$message.error('文件上传失败!');
            this.fileList = fileList;
        },
        submitUpload() {
            if (!this.selectedFile) {
                this.$message.error('请先选择一个文件!');
                return;
            }

            const formData = new FormData();
            formData.append('file', this.selectedFile, this.selectedFile.name);

            axios.post('http://localhost:8000/file/upload', formData)
                .then(response => {
                    this.handleSuccess(response.data, this.selectedFile, this.fileList);
                })
                .catch(error => {
                    this.handleError(error, this.selectedFile, this.fileList);
                });
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

.upload-demo .el-upload__tip {
    color: #999;
}
</style>