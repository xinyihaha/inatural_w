# iNaturalist 图片上传与分类工具

这个工具可以自动上传图片到iNaturalist平台，并使用计算机视觉API获取生物分类信息，包括详细的分类层级（亚科-族-属）。

## 功能特性

- 🔄 **图片上传**: 自动上传图片到iNaturalist并获取photo ID
- 🤖 **智能分类**: 使用iNaturalist计算机视觉API进行物种识别
- 📊 **层级分析**: 提取详细的分类层级信息（亚科、族、属）
- 📁 **批量处理**: 支持批量处理整个文件夹的图片
- 💾 **结果保存**: 自动保存分类结果为JSON格式

## 安装依赖

```bash
pip install -r requirements.txt
```

## 获取API令牌

1. 访问 [iNaturalist API Token页面](https://www.inaturalist.org/users/api_token)
2. 登录你的iNaturalist账户
3. 复制生成的API令牌

## 使用方法

### 方法1：使用示例脚本

运行示例脚本，按提示操作：

```bash
python example_usage.py
```

### 方法2：在代码中使用[弃用]

```python
from inaturalist_uploader import INaturalistUploader

# 初始化上传器
uploader = INaturalistUploader("your_access_token_here")

# 处理单张图片
result = uploader.process_image("path/to/your/image.jpg")

if result:
    print(f"亚科: {result['hierarchy']['subfamily']}")
    print(f"族: {result['hierarchy']['tribe']}")
    print(f"属: {result['hierarchy']['genus']}")
```

## API流程

1. **上传图片** → 获取photo ID
   - 使用iNaturalist上传接口上传图片
   
2. **计算机视觉分析** → 获取分类ID
   - 调用 `https://api.inaturalist.org/v1/computervision/score_image`
   - 获取置信度最高的分类结果
   
3. **详细分类查询** → 获取完整层级
   - 使用pyinaturalist库查询分类详情
   - 提取亚科、族、属信息

## 输出格式

```json
{
  "image_path": "path/to/image.jpg",
  "photo_id": 123456,
  "taxon_id": 876427,
  "taxon_name": "Bundletia moth",
  "common_name": "束带蛾属",
  "score": 0.95,
  "hierarchy": {
    "subfamily": "Pyralinae-螟蛾亚科",
    "tribe": "Pyralini-螟蛾族", 
    "genus": "Bundletia-束带蛾属"
  }
}
```

## 文件说明

- `inaturalist_uploader.py` - 主要功能类
- `example_usage.py` - 使用示例和批量处理
- `up_and_class/idea.py` - API接口说明文档
- `verify_token.py` - API令牌验证工具
- `upload_and_classify.py` - 原有实现（参考）

## 注意事项

- 需要有效的iNaturalist API令牌
- 建议在批量处理时添加延迟避免API频率限制
- 支持的图片格式：JPG, JPEG, PNG, BMP, TIFF
- 分类结果依赖于iNaturalist的计算机视觉模型准确性

## 错误处理

- 自动处理网络超时和API错误
- 详细的错误日志输出
- 图片格式验证
- API响应格式检查 

# 鳞翅目：
- 路径：D:\婆罗洲\001-鳞翅目-整理完毕-待上传\01-鳞翅目-分类完成\01-target
- 文件说明：3,663 个文件，862 个文件夹
  
- 路径：D:\婆罗洲\001-鳞翅目-整理完毕-待上传\01-鳞翅目-分类完成\02-无法分辨
- 无法分辨什么分类，统一为：鳞翅目

- 路径：D:\婆罗洲\001-鳞翅目-整理完毕-待上传\01-鳞翅目-分类完成\03-合成待分离
- 需要检测上传哪只，只能靠w老师肉眼检测了
  






  