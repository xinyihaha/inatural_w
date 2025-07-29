import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
from PIL import Image
import io
from pyinaturalist import *
from pyinaturalist import ClientSession

# 获取apiKey：https://www.inaturalist.org/users/api_token

class INatClassifier:
    def __init__(self, source_dir: str, base_output_dir: str):
        """初始化分类器
        
        Args:
            source_dir: 源图片目录
            base_output_dir: 分类后的输出目录基础路径
        """
        self.source_dir = Path(source_dir)
        self.base_output_dir = Path(base_output_dir)
        self.supported_extensions = ('.jpg', '.jpeg', '.png')
        
        # 确保输出目录存在
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        
    def get_image_files(self) -> List[Path]:
        """获取源目录下的所有图片文件"""
        image_files = []
        for ext in self.supported_extensions:
            image_files.extend(self.source_dir.glob(f'**/*{ext}'))
        return image_files
    
    def upload_and_classify(self, access_token: str) -> None:
        """上传图片到iNaturalist并获取分类信息"""
        # 创建一个超时时间更长的会话
        session = ClientSession(timeout=300)
        image_files = self.get_image_files()
        
        for img_path in image_files:
            try:
                # 检查图片是否存在且可读
                if not img_path.exists():
                    print(f'警告：图片 {img_path} 不存在')
                    continue
                    
                try:
                    with Image.open(img_path) as img:
                        img.verify()
                except Exception as e:
                    print(f'警告：图片 {img_path} 无法读取: {str(e)}')
                    continue

                # 调用计算机视觉分类接口
                print(f'正在获取图片分类: {img_path}...')
                response = session.post(
                    'https://api.inaturalist.org/v1/computervision/score_image',
                    headers={'Authorization': f'Bearer {access_token}'},
                    files={'image': open(img_path, 'rb')}
                )
                
                # 检查响应格式
                if not isinstance(response.json(), dict):
                    print(f'警告：图片 {img_path} 分类失败，API返回格式错误')
                    print(f'API响应: {response.text}')
                    continue
                
                response_data = response.json()
                print(f'API完整响应: {response_data}')
                
                # 获取最佳匹配结果
                results = response_data.get('results', [])
                if not results:
                    print(f'警告：图片 {img_path} 分类失败，未返回结果')
                    continue
                    
                print(f'分类结果: {results}')
                best_match = max(results, key=lambda x: x.get('score', 0))
                taxon = best_match.get('taxon')
                
                # 检查分类信息
                if not taxon:
                    print(f'警告：图片 {img_path} 的分类信息为空')
                    continue
                    
                # 获取亚科和属信息
                subfamily = self._get_subfamily(taxon)
                genus = self._get_genus(taxon)
                
                if not subfamily:
                    print(f'警告：图片 {img_path} 未能获取亚科信息')
                    continue
                    
                if not genus:
                    print(f'警告：图片 {img_path} 未能获取属信息')
                    continue
                
                # 创建分类目录
                subfamily_dir = self._create_taxon_dir(subfamily, is_subfamily=True)
                genus_dir = subfamily_dir / self._format_taxon_name(genus)
                genus_dir.mkdir(exist_ok=True)
                
                # 移动图片到对应目录
                dest_path = genus_dir / img_path.name
                shutil.copy2(img_path, dest_path)
                print(f'已将图片 {img_path.name} 分类到 {genus_dir}')

            except Exception as e:
                print(f'处理图片 {img_path} 时出错: {str(e)}')
                if '500 Server Error' in str(e):
                    print('500错误可能原因：')
                    print('1. iNaturalist服务器临时问题')
                    print('2. 上传的图片格式或大小不符合要求')
                    print('3. API请求频率过高')
                    print('建议：稍后重试或检查图片格式')
    
    def _get_subfamily(self, taxon: Dict) -> Dict:
        """获取亚科信息"""
        ancestors = taxon.get('ancestors', [])
        for ancestor in ancestors:
            if ancestor.get('rank') == 'subfamily':
                return ancestor
        return None
    
    def _get_genus(self, taxon: Dict) -> Dict:
        """获取属信息"""
        ancestors = taxon.get('ancestors', [])
        for ancestor in ancestors:
            if ancestor.get('rank') == 'genus':
                return ancestor
        return None
    
    def _format_taxon_name(self, taxon: Dict) -> str:
        """格式化分类单元名称: 英文名称-中文名称"""
        english_name = taxon.get('name', '')
        chinese_name = taxon.get('preferred_common_name', '')
        if chinese_name:
            return f'{english_name}-{chinese_name}'
        return english_name
    
    def _create_taxon_dir(self, taxon: Dict, is_subfamily: bool = False) -> Path:
        """创建分类目录"""
        dir_name = self._format_taxon_name(taxon)
        dir_path = self.base_output_dir / dir_name
        dir_path.mkdir(exist_ok=True)
        return dir_path

def main():
    # 配置参数
    # SOURCE_DIR = r'D:\婆罗洲\001-整理中-sxy\鳞翅目'
    # OUTPUT_DIR = r'D:\婆罗洲\001-整理中-sxy\鳞翅目_分类'
    SOURCE_DIR = r'D:\婆罗洲\001-整理中-sxy\Test_APi\origin'
    OUTPUT_DIR = r'D:\婆罗洲\001-整理中-sxy\Test_APi\target'
    # 获取访问令牌 (需要先在 iNaturalist 创建应用获取)
    access_token = "eyJhbGciOiJIUzUxMiJ9.eyJ1c2VyX2lkIjo3NTA4ODg0LCJleHAiOjE3NTE4ODA5NzN9.am7-4A1qw4aJRDFyhE-NQxNkwt475jEj7wXEcftTfqYEb8X9az7oN5gbUUAZZf9NOvsSfszhD89cNkrUcpbi8Q"
    
    # 初始化分类器并执行分类
    classifier = INatClassifier(SOURCE_DIR, OUTPUT_DIR)
    classifier.upload_and_classify(access_token)

if __name__ == '__main__':
    main()