import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

# 设置页面配置
st.set_page_config(
    page_title="企业数字化转型指数查询系统",
    page_icon="📊",
    layout="wide"
)

# 页面标题
st.title("📊 企业数字化转型指数查询系统")
st.markdown("### 查询企业历年数字化转型指数趋势")

# 读取数据
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('数字化转型指数合并数据_带行业信息.xlsx')
        return df
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return None

df = load_data()

if df is not None:
    # 数据预处理
    df['股票代码_str'] = df['股票代码'].astype(str).str.zfill(6)  # 股票代码补零到6位
    
    # 获取唯一的股票代码和企业名称映射
    stock_company_map = df[['股票代码_str', '企业名称']].drop_duplicates()
    
    # 侧边栏 - 查询条件
    st.sidebar.header("查询条件")
    
    # 第一个企业查询方式选择
    query_method1 = st.sidebar.radio("第一个企业查询方式", ["股票代码", "企业名称"])
    
    # 根据选择的查询方式显示输入框
    if query_method1 == "股票代码":
        stock_code_input = st.sidebar.text_input("请输入股票代码 (6位数字)", "")
        company_name_input = ""
    else:
        # 获取所有企业名称
        all_companies = sorted(df['企业名称'].unique())
        company_name_input = st.sidebar.selectbox("请选择企业名称", [""] + all_companies)
        stock_code_input = ""
    
    # 第二个企业查询方式选择（可选）
    query_method2 = st.sidebar.radio("第二个企业查询方式（可选）", ["股票代码", "企业名称"])
    
    # 根据选择的查询方式显示输入框
    if query_method2 == "股票代码":
        stock_code_input2 = st.sidebar.text_input("请输入股票代码 (6位数字) - 同行业对比", "")
        company_name_input2 = ""
    else:
        # 获取所有企业名称
        all_companies = sorted(df['企业名称'].unique())
        company_name_input2 = st.sidebar.selectbox("请选择企业名称 - 同行业对比", [""] + all_companies)
        stock_code_input2 = ""
    
    # 年份选择
    all_years = sorted(df['年份'].unique())
    selected_year = st.sidebar.selectbox("选择年份", all_years, index=len(all_years)-1)
    
    # 显示数据概览
    st.sidebar.subheader("数据概览")
    st.sidebar.write(f"企业数量: {df['股票代码'].nunique()}")
    st.sidebar.write(f"时间跨度: {df['年份'].min()} - {df['年份'].max()}")
    st.sidebar.write(f"总记录数: {len(df)}")
    
    # 主页面内容
    if stock_code_input or company_name_input:
        # 查询企业数据
        if stock_code_input:
            # 验证股票代码格式
            if not re.match(r'^\d{6}$', stock_code_input):
                st.error("请输入6位数字的股票代码")
                company_data = None
            else:
                # 查询企业数据
                company_data = df[df['股票代码_str'] == stock_code_input]
        else:
            # 通过企业名称查询
            company_data = df[df['企业名称'] == company_name_input]
            
            if company_data.empty:
                if stock_code_input:
                    st.error(f"未找到股票代码为 {stock_code_input} 的企业数据")
                else:
                    st.error(f"未找到企业名称为 {company_name_input} 的企业数据")
            else:
                # 获取企业基本信息
                company_name = company_data['企业名称'].iloc[0]
                industry_code = company_data['行业代码'].iloc[0]
                industry_name = company_data['行业名称'].iloc[0].strip()
                
                # 显示企业信息
                st.subheader(f"🏢 {company_name} ({stock_code_input}) - {industry_name}")
                
                # 处理第二个企业
                company_data2 = None
                company_name2 = None
                stock_code2 = ""
                
                if stock_code_input2 or company_name_input2:
                    # 查询第二个企业数据
                    if stock_code_input2:
                        # 验证股票代码格式
                        if not re.match(r'^\d{6}$', stock_code_input2):
                            st.error("请输入6位数字的股票代码")
                            company_data2 = None
                        else:
                            # 查询企业数据
                            company_data2 = df[df['股票代码_str'] == stock_code_input2]
                            stock_code2 = stock_code_input2
                    else:
                        # 通过企业名称查询
                        company_data2 = df[df['企业名称'] == company_name_input2]
                        if not company_data2.empty:
                            stock_code2 = company_data2['股票代码_str'].iloc[0]
                        else:
                            stock_code2 = ""
                    
                    if company_data2.empty:
                        if stock_code_input2:
                            st.error(f"未找到股票代码为 {stock_code_input2} 的企业数据")
                        else:
                            st.error(f"未找到企业名称为 {company_name_input2} 的企业数据")
                        company_data2 = None
                    else:
                        # 检查是否同行业
                        industry_code2 = company_data2['行业代码'].iloc[0]
                        if industry_code2 != industry_code:
                            if stock_code_input2:
                                st.error(f"股票代码 {stock_code_input2} 的企业与 {company_name} 不属于同一行业")
                            else:
                                st.error(f"企业 {company_name_input2} 与 {company_name} 不属于同一行业")
                            company_data2 = None
                        else:
                            company_name2 = company_data2['企业名称'].iloc[0]
                            st.subheader(f"🏢 {company_name2} ({stock_code2}) - {industry_name}")
                
                # 显示选定年份的数据
                col1, col2 = st.columns(2)
                
                with col1:
                    year_data = company_data[company_data['年份'] == selected_year]
                    if year_data.empty:
                        st.warning(f"{company_name} 在 {selected_year} 年没有数据")
                    else:
                        digit_index = year_data['数字化转型指数'].iloc[0]
                        st.metric(label=f"{company_name} - {selected_year}年数字化转型指数", value=digit_index)
                
                with col2:
                    if company_data2 is not None:
                        year_data2 = company_data2[company_data2['年份'] == selected_year]
                        if year_data2.empty:
                            st.warning(f"{company_name2} 在 {selected_year} 年没有数据")
                        else:
                            digit_index2 = year_data2['数字化转型指数'].iloc[0]
                            st.metric(label=f"{company_name2} - {selected_year}年数字化转型指数", value=digit_index2)
                
                # 计算行业平均指数
                industry_data = df[df['行业代码'] == industry_code]
                industry_avg = industry_data.groupby('年份')['数字化转型指数'].mean().reset_index()
                industry_avg.columns = ['年份', '行业平均指数']
                
                # 显示历年趋势图
                st.subheader("📈 历年数字化转型指数趋势对比")
                
                # 准备趋势图数据
                trend_data1 = company_data.sort_values('年份')[['年份', '数字化转型指数']]
                
                # 设置中文显示
                plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']  # 中文字体
                plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号
                
                # 创建图表
                fig, ax = plt.subplots(figsize=(12, 6))
                
                # 获取第一个企业的股票代码用于显示
                if stock_code_input:
                    display_code1 = stock_code_input
                else:
                    display_code1 = company_data['股票代码_str'].iloc[0]
                
                # 绘制第一个企业的折线
                ax.plot(trend_data1['年份'], trend_data1['数字化转型指数'], marker='o', linewidth=2, markersize=8, label=f'{company_name} ({display_code1})')
                
                # 绘制第二个企业的折线（如果有）
                if company_data2 is not None:
                    trend_data2 = company_data2.sort_values('年份')[['年份', '数字化转型指数']]
                    ax.plot(trend_data2['年份'], trend_data2['数字化转型指数'], marker='s', linewidth=2, markersize=8, label=f'{company_name2} ({stock_code2})')
                
                # 绘制行业平均指数折线
                ax.plot(industry_avg['年份'], industry_avg['行业平均指数'], marker='^', linewidth=2, markersize=8, linestyle='--', color='gray', label=f'{industry_name} 行业平均')
                
                # 高亮显示选定年份
                if not year_data.empty:
                    digit_index = year_data['数字化转型指数'].iloc[0]
                    ax.scatter(selected_year, digit_index, color='red', s=150, zorder=5)
                
                if company_data2 is not None and not year_data2.empty:
                    digit_index2 = year_data2['数字化转型指数'].iloc[0]
                    ax.scatter(selected_year, digit_index2, color='blue', s=150, zorder=5)
                
                # 设置图表属性
                ax.set_title(f'{industry_name} - 数字化转型指数趋势对比', fontsize=16, fontweight='bold')
                ax.set_xlabel('年份', fontsize=14)
                ax.set_ylabel('数字化转型指数', fontsize=14)
                ax.grid(True, linestyle='--', alpha=0.7)
                
                # 设置y轴范围
                all_data = pd.concat([trend_data1[['年份', '数字化转型指数']], industry_avg.rename(columns={'行业平均指数': '数字化转型指数'})])
                if company_data2 is not None:
                    all_data = pd.concat([all_data, trend_data2[['年份', '数字化转型指数']]])
                max_val = all_data['数字化转型指数'].max()
                ax.set_ylim(0, max(max_val * 1.1, 10))  # 确保y轴有足够空间
                
                # 添加图例
                ax.legend(fontsize=12)
                
                # 优化x轴显示
                years = sorted(all_data['年份'].unique())
                if len(years) > 10:
                    step = len(years) // 10
                    ax.set_xticks(years[::step])
                else:
                    ax.set_xticks(years)
                
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                # 显示图表
                st.pyplot(fig)
                
                # 显示数据表格
                st.subheader("📊 历年数据详情")
                
                # 获取第一个企业的股票代码用于显示
                if stock_code_input:
                    display_code1 = stock_code_input
                else:
                    display_code1 = company_data['股票代码_str'].iloc[0]
                
                # 合并数据表格
                result_table = trend_data1.copy()
                result_table = result_table.rename(columns={'数字化转型指数': f'{company_name} ({display_code1})'})
                
                # 合并第二个企业数据（如果有）
                if company_data2 is not None:
                    trend_data2 = company_data2.sort_values('年份')[['年份', '数字化转型指数']]
                    trend_data2 = trend_data2.rename(columns={'数字化转型指数': f'{company_name2} ({stock_code2})'})
                    result_table = pd.merge(result_table, trend_data2, on='年份', how='outer')
                
                # 合并行业平均数据
                result_table = pd.merge(result_table, industry_avg, on='年份', how='outer')
                
                # 排序并显示
                result_table = result_table.sort_values('年份')
                st.dataframe(result_table, use_container_width=True)
    
    else:
        # 未输入股票代码时显示示例企业
        st.info("请在左侧输入6位股票代码进行查询")
        st.subheader("热门企业示例")
        
        # 选择一些有代表性的企业
        sample_companies = [
            ('600036', '招商银行'),
            ('600519', '贵州茅台'), 
            ('000858', '五粮液'),
            ('000333', '美的集团'),
            ('000651', '格力电器'),
            ('601318', '中国平安'),
            ('600030', '中信证券'),
            ('601166', '兴业银行'),
            ('600000', '浦发银行'),
            ('601398', '工商银行')
        ]
        
        # 显示示例企业表格
        sample_df = pd.DataFrame(sample_companies, columns=['股票代码', '企业名称'])
        st.dataframe(sample_df, use_container_width=True)

# 页脚
st.markdown("---")
st.markdown("© 2024 企业数字化转型指数查询系统 | 数据来源：数字化转型指数合并数据")