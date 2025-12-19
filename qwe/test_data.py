import pandas as pd

try:
    # 读取Excel文件
    df = pd.read_excel('数字化转型指数合并数据.xlsx')
    print('数据加载成功！')
    print('\n数据形状:', df.shape)
    print('\n列名:', df.columns.tolist())
    print('\n前5行数据:\n', df.head())
    print('\n数据类型:\n', df.dtypes)
    
    # 检查是否有空值
    print('\n空值情况:\n', df.isnull().sum())
    
    # 获取所有唯一值的列
    for col in df.columns:
        if df[col].nunique() < 20:
            print(f'\n{col}的唯一值: {sorted(df[col].unique().tolist())}')
            
except Exception as e:
    print(f'发生错误: {str(e)}')
