import os
import shutil
from pathlib import Path
from typing import List, Optional, Callable
import fnmatch
import time


class FileMover:
    """通用文件移动工具类"""
    
    def __init__(self, source_dir: str, target_dir: str):
        """
        初始化文件移动器
        
        Args:
            source_dir: 源文件目录
            target_dir: 目标文件目录
        """
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        
        # 确保源目录存在
        if not self.source_dir.exists():
            raise FileNotFoundError(f"源目录不存在: {source_dir}")
        
        # 创建目标目录
        self.target_dir.mkdir(parents=True, exist_ok=True)
        
        self.moved_count = 0
        self.skipped_count = 0
        self.error_count = 0
        
    def move_single_file(self, source_file: str, target_file: str, overwrite: bool = False) -> bool:
        """
        移动单个文件
        
        Args:
            source_file: 源文件路径
            target_file: 目标文件路径
            overwrite: 是否覆盖目标文件
            
        Returns:
            bool: 移动是否成功
        """
        try:
            source_path = Path(source_file)
            target_path = Path(target_file)
            
            # 检查源文件是否存在
            if not source_path.exists():
                print(f"❌ 源文件不存在: {source_file}")
                self.error_count += 1
                return False
            
            # 创建目标目录
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 检查目标文件是否存在
            if target_path.exists() and not overwrite:
                print(f"⚠️ 目标文件已存在，跳过: {target_file}")
                self.skipped_count += 1
                return False
            
            # 移动文件
            shutil.move(str(source_path), str(target_path))
            print(f"✅ 移动成功: {source_path.name} -> {target_path}")
            self.moved_count += 1
            return True
            
        except Exception as e:
            print(f"❌ 移动失败: {source_file} -> {target_file} (错误: {str(e)})")
            self.error_count += 1
            return False
    
    def move_files_by_pattern(self, pattern: str = "*", overwrite: bool = False, keep_structure: bool = True) -> None:
        """
        按文件模式移动文件
        
        Args:
            pattern: 文件匹配模式 (如 "*.jpg", "*.txt" 等)
            overwrite: 是否覆盖目标文件
            keep_structure: 是否保持目录结构
        """
        print(f"📁 开始移动文件，模式: {pattern}")
        print(f"源目录: {self.source_dir}")
        print(f"目标目录: {self.target_dir}")
        print("=" * 60)
        
        # 查找匹配的文件
        if keep_structure:
            # 递归查找所有匹配的文件
            for source_file in self.source_dir.rglob(pattern):
                if source_file.is_file():
                    # 保持相对路径结构
                    relative_path = source_file.relative_to(self.source_dir)
                    target_file = self.target_dir / relative_path
                    self.move_single_file(str(source_file), str(target_file), overwrite)
        else:
            # 只查找当前目录层级的文件
            for source_file in self.source_dir.glob(pattern):
                if source_file.is_file():
                    target_file = self.target_dir / source_file.name
                    self.move_single_file(str(source_file), str(target_file), overwrite)
        
        self._print_summary()
    
    def move_files_by_extension(self, extensions: List[str], overwrite: bool = False, keep_structure: bool = True) -> None:
        """
        按文件扩展名移动文件
        
        Args:
            extensions: 文件扩展名列表 (如 ['.jpg', '.png', '.gif'])
            overwrite: 是否覆盖目标文件
            keep_structure: 是否保持目录结构
        """
        print(f"📁 开始移动文件，扩展名: {extensions}")
        print(f"源目录: {self.source_dir}")
        print(f"目标目录: {self.target_dir}")
        print("=" * 60)
        
        for ext in extensions:
            pattern = f"*{ext}" if not ext.startswith('.') else f"*{ext}"
            
            if keep_structure:
                for source_file in self.source_dir.rglob(pattern):
                    if source_file.is_file():
                        relative_path = source_file.relative_to(self.source_dir)
                        target_file = self.target_dir / relative_path
                        self.move_single_file(str(source_file), str(target_file), overwrite)
            else:
                for source_file in self.source_dir.glob(pattern):
                    if source_file.is_file():
                        target_file = self.target_dir / source_file.name
                        self.move_single_file(str(source_file), str(target_file), overwrite)
        
        self._print_summary()
    
    def move_files_by_filter(self, filter_func: Callable[[Path], bool], overwrite: bool = False, keep_structure: bool = True) -> None:
        """
        按自定义过滤条件移动文件
        
        Args:
            filter_func: 文件过滤函数，接收Path对象，返回True表示需要移动
            overwrite: 是否覆盖目标文件
            keep_structure: 是否保持目录结构
        """
        print(f"📁 开始移动文件，使用自定义过滤器")
        print(f"源目录: {self.source_dir}")
        print(f"目标目录: {self.target_dir}")
        print("=" * 60)
        
        if keep_structure:
            for source_file in self.source_dir.rglob("*"):
                if source_file.is_file() and filter_func(source_file):
                    relative_path = source_file.relative_to(self.source_dir)
                    target_file = self.target_dir / relative_path
                    self.move_single_file(str(source_file), str(target_file), overwrite)
        else:
            for source_file in self.source_dir.iterdir():
                if source_file.is_file() and filter_func(source_file):
                    target_file = self.target_dir / source_file.name
                    self.move_single_file(str(source_file), str(target_file), overwrite)
        
        self._print_summary()
    
    def move_files_to_subdirs_by_extension(self, overwrite: bool = False) -> None:
        """
        按扩展名将文件移动到不同的子目录
        例如: .jpg文件移动到images/目录，.txt文件移动到texts/目录
        
        Args:
            overwrite: 是否覆盖目标文件
        """
        print(f"📁 开始按扩展名分类移动文件")
        print(f"源目录: {self.source_dir}")
        print(f"目标目录: {self.target_dir}")
        print("=" * 60)
        
        # 扩展名到子目录的映射
        ext_to_subdir = {
            '.jpg': 'images', '.jpeg': 'images', '.png': 'images', '.gif': 'images', '.bmp': 'images', '.tiff': 'images',
            '.txt': 'texts', '.doc': 'documents', '.docx': 'documents', '.pdf': 'documents',
            '.mp4': 'videos', '.avi': 'videos', '.mov': 'videos', '.mkv': 'videos',
            '.mp3': 'audio', '.wav': 'audio', '.flac': 'audio',
            '.zip': 'archives', '.rar': 'archives', '.7z': 'archives',
            '.py': 'code', '.js': 'code', '.html': 'code', '.css': 'code'
        }
        
        for source_file in self.source_dir.iterdir():
            if source_file.is_file():
                ext = source_file.suffix.lower()
                subdir = ext_to_subdir.get(ext, 'others')
                
                target_subdir = self.target_dir / subdir
                target_file = target_subdir / source_file.name
                
                self.move_single_file(str(source_file), str(target_file), overwrite)
        
        self._print_summary()
    
    def move_files_by_size(self, max_size_mb: Optional[float] = None, min_size_mb: Optional[float] = None, 
                          overwrite: bool = False, keep_structure: bool = True) -> None:
        """
        按文件大小移动文件
        
        Args:
            max_size_mb: 最大文件大小(MB)
            min_size_mb: 最小文件大小(MB) 
            overwrite: 是否覆盖目标文件
            keep_structure: 是否保持目录结构
        """
        print(f"📁 开始按文件大小移动文件")
        if max_size_mb:
            print(f"最大文件大小: {max_size_mb} MB")
        if min_size_mb:
            print(f"最小文件大小: {min_size_mb} MB")
        print(f"源目录: {self.source_dir}")
        print(f"目标目录: {self.target_dir}")
        print("=" * 60)
        
        for source_file in self.source_dir.rglob("*") if keep_structure else self.source_dir.iterdir():
            if source_file.is_file():
                file_size_mb = source_file.stat().st_size / (1024 * 1024)
                
                # 检查文件大小是否符合条件
                if max_size_mb and file_size_mb > max_size_mb:
                    continue
                if min_size_mb and file_size_mb < min_size_mb:
                    continue
                
                if keep_structure:
                    relative_path = source_file.relative_to(self.source_dir)
                    target_file = self.target_dir / relative_path
                else:
                    target_file = self.target_dir / source_file.name
                
                print(f"📋 文件大小: {file_size_mb:.2f} MB")
                self.move_single_file(str(source_file), str(target_file), overwrite)
        
        self._print_summary()
    
    def _print_summary(self):
        """打印移动结果摘要"""
        print("\n" + "=" * 60)
        print("📊 文件移动结果统计")
        print("=" * 60)
        print(f"✅ 成功移动: {self.moved_count} 个文件")
        print(f"⚠️ 跳过移动: {self.skipped_count} 个文件")
        print(f"❌ 移动失败: {self.error_count} 个文件")
        print(f"📍 目标目录: {self.target_dir}")
        
        # 重置计数器
        self.moved_count = 0
        self.skipped_count = 0
        self.error_count = 0

    def move_files_keep_prefix_before_hyphen(self, overwrite: bool = False) -> None:
        """
        移动文件并保留目录名称中第一个连字符(-)前的部分作为目标目录名
        
        Args:
            overwrite: 是否覆盖目标文件
        """
        print(f"📁 开始移动文件，保留目录名前缀")
        print(f"源目录: {self.source_dir}")
        print(f"目标目录: {self.target_dir}")
        print("=" * 60)
        
        for source_file in self.source_dir.rglob("*"):
            if source_file.is_file():
                # 获取相对路径
                relative_path = source_file.relative_to(self.source_dir)
                
                # 处理每个目录层级
                new_parts = []
                for part in relative_path.parts[:-1]:  # 排除文件名部分
                    # 保留第一个连字符前的部分
                    prefix = part.split('-')[0].strip()
                    new_parts.append(prefix)
                
                # 构建新路径
                new_relative_path = Path(*new_parts) / relative_path.name
                target_file = self.target_dir / new_relative_path
                
                self.move_single_file(str(source_file), str(target_file), overwrite)
        
        self._print_summary()

    def remove_empty_dirs(self) -> None:
        """
        删除源目录中所有不包含文件的空目录
        
        递归检查源目录下的所有子目录，如果目录中不包含任何文件(包括子目录中的文件)，
        则删除该目录
        """
        print(f"🧹 开始清理空目录")
        print(f"源目录: {self.source_dir}")
        print("=" * 60)
        
        removed_count = 0
        
        # 从最深层目录开始检查
        for dir_path in sorted(self.source_dir.rglob("*"), key=lambda p: len(p.parts), reverse=True):
            if dir_path.is_dir():
                # 检查目录是否为空
                has_files = any(file.is_file() for file in dir_path.rglob("*"))
                if not has_files:
                    try:
                        dir_path.rmdir()
                        print(f"🗑️ 删除空目录: {dir_path}")
                        removed_count += 1
                    except OSError as e:
                        print(f"❌ 删除目录失败: {dir_path} (错误: {str(e)})")
        
        print("\n" + "=" * 60)
        print("📊 空目录清理结果")
        print("=" * 60)
        print(f"✅ 成功删除: {removed_count} 个空目录")

def move_all_files(source_dir: str, target_dir: str, overwrite: bool = False, keep_structure: bool = True):
    """
    简单函数：移动目录下的所有文件
    
    Args:
        source_dir: 源目录
        target_dir: 目标目录
        overwrite: 是否覆盖目标文件
        keep_structure: 是否保持目录结构
    """
    mover = FileMover(source_dir, target_dir)
    mover.move_files_by_pattern("*", overwrite, keep_structure)


def move_images(source_dir: str, target_dir: str, overwrite: bool = False, keep_structure: bool = True):
    """
    简单函数：移动图片文件
    
    Args:
        source_dir: 源目录
        target_dir: 目标目录
        overwrite: 是否覆盖目标文件
        keep_structure: 是否保持目录结构
    """
    mover = FileMover(source_dir, target_dir)
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp','orf']
    mover.move_files_by_extension(image_extensions, overwrite, keep_structure)


def example_usage():
    """使用示例"""
    print("🔧 文件移动工具使用示例")
    print("=" * 50)
    
    # 从用户输入获取目录路径
    source_dir = input("请输入源目录路径: ").strip()
    target_dir = input("请输入目标目录路径: ").strip()
    
    # 检查目录是否存在
    if not os.path.exists(source_dir):
        print(f"❌ 源目录不存在: {source_dir}")
        print("请修改 example_usage() 函数中的路径配置")
        return
    
    try:
        # 创建文件移动器
        mover = FileMover(source_dir, target_dir)
        
        print("\n选择移动模式:")
        print("1. 移动所有文件")
        print("2. 只移动图片文件")
        print("3. 按扩展名分类移动")
        print("4. 按文件大小移动")
        print("5. 自定义过滤器移动")
        print("6. 保留目录名前缀移动")
        print("7. 清理空目录")
        
        choice = input("\n请输入选择 (1-7): ").strip()
        
        if choice == "1":
            mover.move_files_by_pattern("*", overwrite=False, keep_structure=True)
            
        elif choice == "2":
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', 'orf']
            mover.move_files_by_extension(image_extensions, overwrite=False, keep_structure=True)
            
        elif choice == "3":
            mover.move_files_to_subdirs_by_extension(overwrite=False)
            
        elif choice == "4":
            max_size = float(input("输入最大文件大小(MB，留空表示无限制): ") or "0") or None
            min_size = float(input("输入最小文件大小(MB，留空表示无限制): ") or "0") or None
            mover.move_files_by_size(max_size, min_size, overwrite=False, keep_structure=True)
            
        elif choice == "5":
            # 示例：移动修改时间在7天内的文件
            def recent_files_filter(file_path: Path) -> bool:
                file_time = file_path.stat().st_mtime
                current_time = time.time()
                days_old = (current_time - file_time) / (24 * 60 * 60)
                return days_old <= 7
            
            mover.move_files_by_filter(recent_files_filter, overwrite=False, keep_structure=True)
            
        elif choice == "6":
            mover.move_files_keep_prefix_before_hyphen(overwrite=False)

        elif choice == "7":
            mover.remove_empty_dirs()
        
        else:
            print("❌ 无效选择")
            
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")



if __name__ == "__main__":
    example_usage()