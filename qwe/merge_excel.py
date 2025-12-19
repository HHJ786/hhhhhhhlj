import pandas as pd

# 设置文件路径
excel_file1 = r"c:\Users\HUAWEI\Desktop\qwe\数字化转型指数合并数据.xlsx"
excel_file2 = r"c:\Users\HUAWEI\Desktop\qwe\最终数据dta格式-上市公司年度行业代码至2021.xlsx"
output_file = r"c:\Users\HUAWEI\Desktop\qwe\数字化转型指数合并数据_带行业信息.xlsx"

def merge_excel_files():
    try:
        print("开始执行数据合并任务...")
        
        # 读取第一张Excel表
        df1 = pd.read_excel(excel_file1)
        print(f"✓ 成功读取第一张表：{df1.shape[0]}行 × {df1.shape[1]}列")
        
        # 读取第二张Excel表
        df2 = pd.read_excel(excel_file2)
        print(f"✓ 成功读取第二张表：{df2.shape[0]}行 × {df2.shape[1]}列")
        
        # 数据预处理：将关键字段转换为统一格式
        print("\n开始数据预处理...")
        
        # 将股票代码转换为字符串格式（不补零，直接转换）
        df1['股票代码_str'] = df1['股票代码'].astype(str)
        df2['股票代码_str'] = df2['股票代码全称'].astype(str)  # 使用股票代码全称
        
        # 重命名第二张表的年度列为年份，保持一致
        df2 = df2.rename(columns={'年度': '年份'})
        
        # 选择需要合并的字段
        df2_selected = df2[['股票代码_str', '年份', '行业代码', '行业名称']]
        
        # 检查是否有重复的股票代码和年份组合（在第二张表中）
        duplicate_count = df2_selected.duplicated(subset=['股票代码_str', '年份']).sum()
        if duplicate_count > 0:
            print(f"⚠ 注意：第二张表中存在{duplicate_count}个重复的股票代码和年份组合，将保留第一个匹配项")
            df2_selected = df2_selected.drop_duplicates(subset=['股票代码_str', '年份'], keep='first')
        
        # 执行合并操作
        print("\n开始执行数据合并...")
        merged_df = pd.merge(
            df1, 
            df2_selected, 
            on=['股票代码_str', '年份'], 
            how='left'  # 使用左连接，保留第一张表的所有数据
        )
        
        # 检查合并结果
        print("\n合并结果分析：")
        print(f"✓ 合并后总记录数：{merged_df.shape[0]}")
        print(f"✓ 成功匹配行业信息的记录数：{merged_df['行业代码'].notna().sum()}")
        print(f"✓ 未匹配到行业信息的记录数：{merged_df['行业代码'].isna().sum()}")
        
        # 计算匹配成功率
        match_rate = merged_df['行业代码'].notna().sum() / merged_df.shape[0] * 100
        print(f"✓ 匹配成功率：{match_rate:.2f}%")
        
        # 删除临时创建的股票代码字符串列
        merged_df = merged_df.drop(columns=['股票代码_str'])
        
        # 保存合并结果到新的Excel文件
        print("\n正在保存合并结果...")
        merged_df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"✓ 合并结果已保存至：{output_file}")
        
        # 显示合并后的前几行数据
        print("\n合并后的数据示例：")
        print(merged_df.head())
        
        print("\n✅ 数据合并任务完成！")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    merge_excel_files()