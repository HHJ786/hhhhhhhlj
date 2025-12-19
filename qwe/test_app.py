import pandas as pd
import re

# 测试数据读取
try:
    df = pd.read_excel('数字化转型指数合并数据_带行业信息.xlsx')
    print('数据读取成功！')
    print('数据列名:', df.columns.tolist())
    print('\n数据行数:', len(df))
    
    # 测试股票代码处理
    df['股票代码_str'] = df['股票代码'].astype(str).str.zfill(6)
    print('\n股票代码处理成功！')
    
    # 测试行业信息
    print('\n行业信息示例:')
    print(df[['行业代码', '行业名称']].head())
    
    # 测试行业平均计算
    industry_code = df['行业代码'].iloc[0]
    industry_data = df[df['行业代码'] == industry_code]
    industry_avg = industry_data.groupby('年份')['数字化转型指数'].mean().reset_index()
    industry_avg.columns = ['年份', '行业平均指数']
    print('\n行业平均指数计算成功！')
    print(industry_avg.head())
    
    print('\n所有测试通过！')
    
except Exception as e:
    print('测试失败:', e)
    import traceback
    traceback.print_exc()