import requests
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from pyinaturalist import get_taxa_by_id, upload_photos
import time


class INaturalistUploader:
    """iNaturalist图片上传和分类器"""
    
    def __init__(self, access_token: str):
        """
        初始化上传器
        
        Args:
            access_token: iNaturalist API访问令牌
        """
        self.access_token = access_token
        self.headers = {'Authorization': f'Bearer {access_token}'}
        self.cv_api_url = 'https://api.inaturalist.org/v1/computervision/score_image'
        
    def upload_image(self, image_path: str) -> Optional[int]:
        """
        上传图片到iNaturalist
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            photo_id: 上传成功后的图片ID，失败返回None
        """
        try:
            print(f"正在上传图片: {image_path}")
            
            # 使用pyinaturalist库上传图片
            response = upload_photos(
                photos=image_path,
                access_token=self.access_token
            )
            
            if isinstance(response, dict) and 'id' in response:
                photo_id = response['id']
                print(f"图片上传成功，ID: {photo_id}")
                return photo_id
            else:
                print(f"图片上传失败: {response}")
                return None
                
        except Exception as e:
            print(f"上传图片时出错: {str(e)}")
            return None
    
    def classify_image(self, image_path: str) -> Optional[Dict]:
        """
        使用计算机视觉API分析图片
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            classification_result: 分类结果字典，失败返回None
        """
        try:
            print(f"正在分析图片: {image_path}")
            
            with open(image_path, 'rb') as image_file:
                files = {'image': image_file}
                response = requests.post(
                    self.cv_api_url,
                    headers=self.headers,
                    files=files,
                    timeout=60
                )
            
            if response.status_code == 200:
                result = response.json()
                print(f"图片分析成功")
                return result
            else:
                print(f"图片分析失败，状态码: {response.status_code}")
                print(f"错误信息: {response.text}")
                return None
                
        except Exception as e:
            print(f"分析图片时出错: {str(e)}")
            return None
    
    def get_best_classification(self, cv_result: Dict) -> Optional[Dict]:
        """
        从计算机视觉结果中获取最佳分类
        
        Args:
            cv_result: 计算机视觉API返回的结果
            
        Returns:
            best_taxon: 最佳分类的taxon信息
        """
        try:
            results = cv_result.get('common_ancestor', [])
            if not results:
                print("没有找到分类结果")
                return None
            
            best_result = dict(results)
            score = best_result.get('score', 0)
            taxon = best_result.get('taxon') if isinstance(best_result, dict) else None
            
            if taxon:
                print(f"最佳分类: {taxon.get('name', 'Unknown')} (得分: {score})")
                return taxon
            else:
                print("分类结果中没有taxon信息")
                return None
                
        except Exception as e:
            print(f"处理分类结果时出错: {str(e)}")
            return None
    
    def get_detailed_taxonomy(self, taxon_id: int) -> Optional[Dict]:
        """
        根据taxon ID获取详细的分类信息
        
        Args:
            taxon_id: 分类单元ID
            
        Returns:
            detailed_info: 详细的分类信息
        """
        try:
            print(f"正在获取分类详情，ID: {taxon_id}")
            
            # 使用pyinaturalist获取分类详情
            response = get_taxa_by_id(taxon_id)
            
            if isinstance(response, dict) and 'results' in response:
                results = response['results']
                if results:
                    taxon_info = results[0]
                    print(f"获取分类详情成功: {taxon_info.get('name', 'Unknown')}")
                    return taxon_info
            
            print("获取分类详情失败")
            return None
            
        except Exception as e:
            print(f"获取分类详情时出错: {str(e)}")
            return None
    
    def extract_hierarchy(self, taxon_info: Dict) -> Dict[str, Optional[str]]:
        """
        从分类信息中提取亚科-族-属层级
        
        Args:
            taxon_info: 完整的分类信息
            
        Returns:
            hierarchy: 包含亚科、族、属信息的字典
        """
        hierarchy = {
            'subfamily': None,
            'tribe': None, 
            'genus': None
        }
        
        try:
            # 从ancestors中查找各个层级
            ancestors = taxon_info.get('ancestors', [])
            
            # 添加当前taxon到ancestors列表末尾，以便检查当前分类
            current_taxon = {
                'id': taxon_info.get('id'),
                'name': taxon_info.get('name'),
                'rank': taxon_info.get('rank'),
                'preferred_common_name': taxon_info.get('preferred_common_name')
            }
            all_taxa = ancestors + [current_taxon]
            
            for taxon in all_taxa:
                rank = taxon.get('rank', '').lower()
                name = taxon.get('name', '')
                if rank == 'family':
                    hierarchy['subfamily'] = name
                elif rank == 'subfamily':
                    hierarchy['subfamily'] = name
                elif rank == 'tribe':
                    hierarchy['tribe'] = name
                elif rank == 'genus':
                    hierarchy['genus'] = name

            print(f"层级信息提取完成:")
            print(f"  亚科: {hierarchy['subfamily']}")
            print(f"  族: {hierarchy['tribe']}")
            print(f"  属: {hierarchy['genus']}")
            
            return hierarchy
            
        except Exception as e:
            print(f"提取层级信息时出错: {str(e)}")
            return hierarchy
    
    def process_image(self, image_path: str) -> Optional[Dict]:
        """
        完整处理图片：上传 -> 分析 -> 获取详细分类信息
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            result: 包含完整分类信息的结果字典
        """
        print(f"\n开始处理图片: {image_path}")
        print("=" * 50)
        photo_id = None
        # # 步骤1：上传图片
        # photo_id = self.upload_image(image_path)
        
        # 步骤2：分析图片分类
        cv_result = self.classify_image(image_path)
        if not cv_result:
            return None
        
        # 步骤3：获取最佳分类
        best_taxon = self.get_best_classification(cv_result)
        if not best_taxon:
            return None
        
        taxon_id = best_taxon.get('id')
        if not taxon_id:
            print("无法获取taxon ID")
            return None
        
        # 步骤4：获取详细分类信息
        detailed_info = self.get_detailed_taxonomy(taxon_id)
        if not detailed_info:
            return None
        
        # 步骤5：提取层级信息
        hierarchy = self.extract_hierarchy(detailed_info)
        
        # 整理最终结果
        result = {
            'image_path': image_path,
            'photo_id': photo_id,
            'taxon_id': taxon_id,
            'taxon_name': best_taxon.get('name'),
            'common_name': best_taxon.get('preferred_common_name'),
            'score': cv_result['common_ancestor'].get('score', 0) if cv_result.get('common_ancestor') else 0,
            'hierarchy': hierarchy,
            # 'full_taxonomy': detailed_info
        }
        
        print(f"\n处理完成！结果:")
        print(f"图片路径: {result['image_path']}")
        print(f"图片ID: {result['photo_id']}")
        print(f"分类名称: {result['taxon_name']}")
        print(f"常用名: {result['common_name']}")
        print(f"置信度: {result['score']:.3f}")
        print(f"亚科: {result['hierarchy']['subfamily']}")
        print(f"族: {result['hierarchy']['tribe']}")
        print(f"属: {result['hierarchy']['genus']}")
        
        return result


def main():
    """示例使用"""
    # 配置访问令牌
    ACCESS_TOKEN = "your_access_token_here"
    
    # 创建上传器实例
    uploader = INaturalistUploader(ACCESS_TOKEN)
    
    # 示例图片路径
    image_path = "path/to/your/image.jpg"
    
    # 处理图片
    result = uploader.process_image(image_path)
    
    if result:
        print("\n" + "=" * 50)
        print("最终分类结果:")
        print(json.dumps(result['hierarchy'], ensure_ascii=False, indent=2))
    else:
        print("图片处理失败")


if __name__ == '__main__':
    main() 