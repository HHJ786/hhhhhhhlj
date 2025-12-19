import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 设置页面配置
st.set_page_config(
    page_title="企业数字化转型指数查询系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 应用标题
st.title("📊 企业数字化转型指数查询系统")

# 文件路径
DATA_FILE = "数字化转型指数合并数据_带行业信息.xlsx"

@st.cache_data
def load_data():
    """加载合并后的Excel数据"""
    try:
        df = pd.read_excel(DATA_FILE)
        # 处理可能的缺失值
        df = df.dropna(subset=['股票代码', '年份', '数字化转型指数'])
        # 确保数据类型正确
        df['股票代码'] = df['股票代码'].astype(str)
        df['年份'] = df['年份'].astype(int)
        return df
    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return None

@st.cache_data
def get_industry_avg(df):
    """计算历年各行业的平均数字化转型指数"""
    if df is None:
        return None
    # 按行业和年份分组计算平均值
    industry_avg = df.groupby(['行业代码', '年份'])['数字化转型指数'].mean().reset_index()
    return industry_avg

@st.cache_data
def get_company_info(df):
    """获取公司基本信息"""
    if df is None:
        return None
    # 获取所有唯一的股票代码和企业名称
    company_info = df[['股票代码', '企业名称', '行业代码', '行业名称']].drop_duplicates()
    return company_info

# 加载数据
st.info("正在加载数据...")
df = load_data()
industry_avg = get_industry_avg(df)
company_info = get_company_info(df)

if df is not None:
    st.success(f"数据加载成功！共包含 {len(df)} 条记录")
    
    # 侧边栏 - 查询参数设置
    st.sidebar.header("🔍 查询参数")
    
    # 股票代码选择
    all_stock_codes = sorted(company_info['股票代码'].unique())
    stock_code = st.sidebar.selectbox(
        "选择股票代码:",
        options=all_stock_codes,
        format_func=lambda x: f"{x} - {company_info[company_info['股票代码'] == x]['企业名称'].iloc[0]}"
    )
    
    # 年份范围选择
    min_year = df['年份'].min()
    max_year = df['年份'].max()
    year_range = st.sidebar.slider(
        "选择年份范围:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1
    )
    
    # 获取选中企业的信息
    selected_company = company_info[company_info['股票代码'] == stock_code].iloc[0]
    company_name = selected_company['企业名称']
    industry_code = selected_company['行业代码']
    industry_name = selected_company['行业名称']
    
    # 主内容区
    st.markdown("---")
    
    # 企业基本信息卡片
    st.header(f"🏢 {company_name} ({stock_code})")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("行业代码", industry_code)
    with col2:
        st.metric("行业名称", industry_name)
    with col3:
        st.metric("数据年份范围", f"{min_year} - {max_year}")
    
    # 筛选数据
    company_data = df[(df['股票代码'] == stock_code) & 
                      (df['年份'] >= year_range[0]) & 
                      (df['年份'] <= year_range[1])]
    
    # 获取行业平均数据
    industry_data = industry_avg[(industry_avg['行业代码'] == industry_code) & 
                                (industry_avg['年份'] >= year_range[0]) & 
                                (industry_avg['年份'] <= year_range[1])]
    
    # 可视化：企业历年数字化转型指数与行业平均对比
    st.subheader("📈 数字化转型指数趋势分析")
    
    if not company_data.empty:
        # 创建图表
        fig = go.Figure()
        
        # 添加企业指数折线
        fig.add_trace(go.Scatter(
            x=company_data['年份'],
            y=company_data['数字化转型指数'],
            mode='lines+markers',
            name=f'{company_name} (企业)',
            line=dict(color='blue', width=2),
            marker=dict(size=6, color='blue')
        ))
        
        # 添加行业平均指数折线
        if not industry_data.empty:
            fig.add_trace(go.Scatter(
                x=industry_data['年份'],
                y=industry_data['数字化转型指数'],
                mode='lines+markers',
                name=f'{industry_name} (行业平均)',
                line=dict(color='red', width=2, dash='dash'),
                marker=dict(size=6, color='red')
            ))
        
        # 更新图表布局
        fig.update_layout(
            title=f"{company_name} 数字化转型指数趋势 (vs {industry_name}行业平均)",
            xaxis_title="年份",
            yaxis_title="数字化转型指数",
            legend_title="指标",
            hovermode="x unified",
            template="plotly_white",
            height=500
        )
        
        # 显示图表
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示详细数据表格
        st.subheader("📋 详细数据")
        st.dataframe(company_data[['年份', '数字化转型指数', '行业代码', '行业名称']], use_container_width=True)
        
        # 统计信息
        st.subheader("📊 统计分析")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_index = company_data['数字化转型指数'].mean()
            st.metric("平均指数", f"{avg_index:.2f}")
        
        with col2:
            max_index = company_data['数字化转型指数'].max()
            max_year = company_data[company_data['数字化转型指数'] == max_index]['年份'].iloc[0]
            st.metric("最高指数", f"{max_index:.2f}", f"年份: {max_year}")
        
        with col3:
            min_index = company_data['数字化转型指数'].min()
            min_year = company_data[company_data['数字化转型指数'] == min_index]['年份'].iloc[0]
            st.metric("最低指数", f"{min_index:.2f}", f"年份: {min_year}")
        
        with col4:
            trend = company_data['数字化转型指数'].pct_change().mean() * 100
            st.metric("年均增长率", f"{trend:.2f}%")
        
    else:
        st.warning("未找到该企业在所选年份范围内的数据")
    
    # 行业分析
    st.subheader("🏭 行业分析")
    
    # 显示行业内所有企业的平均指数对比
    if not industry_data.empty:
        st.write(f"{industry_name}行业历年平均数字化转型指数")
        
        # 行业平均指数趋势图
        fig_industry = px.line(
            industry_data,
            x="年份",
            y="数字化转型指数",
            title=f"{industry_name}行业平均数字化转型指数趋势"
        )
        fig_industry.update_layout(template="plotly_white", height=400)
        st.plotly_chart(fig_industry, use_container_width=True)
    
    # 数据概览
    st.markdown("---")
    st.subheader("📊 数据概览")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"✅ 总企业数: {len(company_info)}")
    with col2:
        st.info(f"📅 年份范围: {min_year} - {max_year}")
    with col3:
        st.info(f"📈 数据记录数: {len(df)}")
    
    # 显示数据样本
    st.write("数据样本:")
    st.dataframe(df.head(), use_container_width=True)

# 页脚
st.markdown("---")
st.footer("© 2024 企业数字化转型指数查询系统 | 基于Streamlit构建")