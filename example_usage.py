"""
iNaturalist图片上传和分类使用示例

此示例演示如何：
1. 上传图片到iNaturalist获取photo ID
2. 使用计算机视觉API分析图片
3. 获取详细分类信息（亚科-族-属）

运行：python example_usage.py
首先访问：https://www.inaturalist.org/users/api_token 获取apiKey
"""

from inaturalist_uploader import INaturalistUploader
import json
import os
from pathlib import Path


def batch_process_images(image_folder: str, access_token: str, output_file: str = "classification_results.json"):
    """
    批量处理图片文件夹中的所有图片
    
    Args:
        image_folder: 包含图片的文件夹路径
        access_token: iNaturalist API访问令牌
        output_file: 结果保存文件路径
    """
    # 检查结果文件是否存在，如果存在则直接读取
    if os.path.exists(output_file):
        print(f"检测到已有结果文件: {output_file}，直接读取...")
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_results = json.load(f)
                print(f"成功读取 {len(existing_results)} 条已有结果")
                return existing_results
        except Exception as e:
            print(f"读取结果文件失败: {str(e)}，将重新处理图片")
          
    # 创建上传器实例
    uploader = INaturalistUploader(access_token)
    
    # 查找所有图片文件(不区分大小写，包含子目录)
    image_folder = Path(image_folder)
    image_files = list(image_folder.rglob('*.[jJ][pP][gG]')) + \
                 list(image_folder.rglob('*.[jJ][pP][eE][gG]')) + \
                 list(image_folder.rglob('*.[pP][nN][gG]')) + \
                 list(image_folder.rglob('*.[bB][mM][pP]')) + \
                 list(image_folder.rglob('*.[tT][iI][fF][fF]'))
    print(f"找到 {len(image_files)} 个图片文件（包含子目录）")
    
    # 存储所有结果
    all_results = []
    
    for i, image_path in enumerate(image_files, 1):
        print(f"\n处理第 {i}/{len(image_files)} 个图片")
        
        # 处理单张图片
        result = uploader.process_image(str(image_path))
        
        if result:
            all_results.append(result)
            print(f"✓ 成功处理: {image_path.name}")
        else:
            print(f"✗ 处理失败: {image_path.name}")
        
        # 添加延迟避免API频率限制
        import time
        time.sleep(2)

        # 每处理10个图片保存一次中间结果
        if i % 10 == 0:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, ensure_ascii=False, indent=2)
            print(f"已保存前 {i} 个图片的处理结果到 {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"已保存前 {len(all_results)} 个图片的处理结果到 {output_file}")
    
    print(f"\n处理完成！共成功处理 {len(all_results)} 张图片")
    print(f"结果已保存到: {output_file}")
    
    return all_results


def single_image_example():
    """单张图片处理示例"""
    # 配置参数
    ACCESS_TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJ1c2VyX2lkIjo3NTA4ODg0LCJleHAiOjE3NTE5NjUxMDF9.YATTtmRJecsGlg2z3zggv-qR8MSJImMaQAH9fHWsRf753GGf22wv5VQqj7OFoAHONTzh6fShL0me-S2brdALiQ"  # 替换为你的实际token
    IMAGE_PATH = r"D:\婆罗洲\001-整理中-sxy\Test_APi\origin\P5060721.JPG"    # 替换为你的图片路径
    
    # 检查图片文件是否存在
    if not os.path.exists(IMAGE_PATH):
        print(f"错误：图片文件不存在: {IMAGE_PATH}")
        return
    
    # 创建上传器实例
    uploader = INaturalistUploader(ACCESS_TOKEN)
    
    # 处理图片
    result = uploader.process_image(IMAGE_PATH)
    
    if result:
        print("\n" + "=" * 60)
        print("🎉 图片处理成功！")
        print("=" * 60)
        
        # 显示分类层级信息
        hierarchy = result['hierarchy']
        print("\n📊 分类层级信息:")
        print(f"  🔸 亚科 (Subfamily): {hierarchy['subfamily'] or '未识别'}")
        print(f"  🔸 族 (Tribe): {hierarchy['tribe'] or '未识别'}")  
        print(f"  🔸 属 (Genus): {hierarchy['genus'] or '未识别'}")
        
        # 显示基本信息
        print(f"\n📋 基本信息:")
        print(f"  🔸 图片ID: {result['photo_id']}")
        print(f"  🔸 分类名称: {result['taxon_name']}")
        print(f"  🔸 常用名: {result['common_name'] or '无'}")
        print(f"  🔸 置信度: {result['score']:.3f}")
        
        # 保存详细结果
        output_file = f"result_{Path(IMAGE_PATH).stem}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 详细结果已保存到: {output_file}")
        
    else:
        print("❌ 图片处理失败")


def format_hierarchy_display(results: list):
    """格式化显示分类层级统计"""
    print("\n" + "=" * 80)
    print("📊 分类统计结果")
    print("=" * 80)
    
    # 统计各层级
    subfamilies = set()
    tribes = set()
    genera = set()
    
    for result in results:
        hierarchy = result['hierarchy']
        if hierarchy['subfamily']:
            subfamilies.add(hierarchy['subfamily'])
        if hierarchy['tribe']:
            tribes.add(hierarchy['tribe'])
        if hierarchy['genus']:
            genera.add(hierarchy['genus'])
    
    print(f"\n📈 统计信息:")
    print(f"  🔸 处理图片总数: {len(results)}")
    print(f"  🔸 发现亚科数量: {len(subfamilies)}")
    print(f"  🔸 发现族数量: {len(tribes)}")
    print(f"  🔸 发现属数量: {len(genera)}")
    
    # 显示具体分类
    if subfamilies:
        print(f"\n🏷️  发现的亚科:")
        for subfamily in sorted(subfamilies):
            print(f"    • {subfamily}")
    
    if tribes:
        print(f"\n🏷️  发现的族:")
        for tribe in sorted(tribes):
            print(f"    • {tribe}")
    
    if genera:
        print(f"\n🏷️  发现的属:")
        for genus in sorted(genera):
            print(f"    • {genus}")


def move_images_by_classification(results: list, target_base_dir: str):
    """
    根据分类结果将图片移动到对应的分类目录中(亚科/族/属)
    
    Args:
        results: 分类结果列表
        target_base_dir: 目标基础目录
    """
    print("\n" + "=" * 80)
    print("📂 开始按分类转移图片")
    print("=" * 80)
    import os
    # 确保目标基础目录存在
    os.makedirs(target_base_dir, exist_ok=True)
    
    moved_count = 0
    skipped_count = 0
    
    for result in results:
        image_path = result['image_path']
        hierarchy = result['hierarchy']
        
        # 构建目标路径: 目标基础目录/亚科/族/属
        subfamily = hierarchy['subfamily'] or "未知亚科"
        tribe = hierarchy['tribe'] or "未知族" 
        genus = hierarchy['genus'] or "未知属"
        
        target_dir = os.path.join(target_base_dir, subfamily, tribe, genus)
        os.makedirs(target_dir, exist_ok=True)
        
        # 获取文件名并构建目标路径
        filename = os.path.basename(image_path)
        target_path = os.path.join(target_dir, filename)
        
        try:
            # 移动文件及同名不同格式的其他文件
            import shutil
            import os
            
            base_name = os.path.splitext(filename)[0]
            source_dir = os.path.dirname(image_path)
            
            shutil.move(image_path, target_path)
            print(f"✅ 已移动: {filename} -> {target_path}")
            moved_count += 1
            
            for file in os.listdir(source_dir):
                if file.startswith(base_name + '.') and file != filename:
                    shutil.move(
                        os.path.join(source_dir, file),
                        os.path.join(target_dir, file)
                    )
                    print(f"✅ 已移动关联文件: {file} -> {os.path.join(target_dir, file)}")
            
            # 更新结果中的图片路径
            result['image_path'] = target_path
            
        except Exception as e:
            print(f"❌ 移动失败: {filename} (错误: {str(e)})")
            skipped_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 转移结果统计:")
    print(f"  ✅ 成功移动: {moved_count} 张")
    print(f"  ❌ 跳过移动: {skipped_count} 张")
    print(f"  📍 目标目录: {target_base_dir}")

def main():
    """主函数"""
    print("🌿 iNaturalist 图片分类工具")
    print("=" * 50)
    
    # 选择模式
    print("\n请选择运行模式:")
    print("1. 单张图片处理")
    print("2. 批量图片处理")
    
    try:
        choice = input("\n请输入选择 (1 或 2): ").strip()
        
        if choice == "1":
            print("\n🔄 运行单张图片处理示例...")
            single_image_example()
            
        elif choice == "2":
            print("\n🔄 运行批量图片处理...")
            
            # 获取配置参数
            access_token = input("请输入你的iNaturalist访问令牌: ").strip()
            image_folder = input("请输入图片文件夹路径: ").strip()
        # 获取目标路径
            target_path = input("请输入分类后的目标文件夹路径: ").strip()
            if not target_path:
                print("❌ 错误：目标路径不能为空")
                return
            
            if not access_token:
                print("❌ 错误：访问令牌不能为空")
                return
                
            if not os.path.exists(image_folder):
                print(f"❌ 错误：文件夹不存在: {image_folder}")
                return
            
            # 批量处理
            results = batch_process_images(image_folder, access_token)
            
            if results:
                format_hierarchy_display(results)                
                move_images_by_classification(results, target_path)
            
        else:
            print("❌ 无效选择")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  用户取消操作")
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")


if __name__ == '__main__':
    main() 