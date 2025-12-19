import streamlit as st
import pandas as pd
import plotly.express as px

# 设置页面标题和布局
st.set_page_config(
    page_title="企业数字化转型指数查询系统",
    page_icon="📊",
    layout="wide"
)

# 页面标题
st.title("📊 企业数字化转型指数查询系统")

# 侧边栏说明
st.sidebar.header("使用说明")
st.sidebar.info(
    "1. 确保Excel文件'数字化转型指数合并数据.xlsx'与应用在同一目录下\n"
    "2. 选择股票代码和年份进行查询\n"
    "3. 查看该企业历年数字化转型指数趋势"
)

# 加载数据
try:
    # 读取Excel文件
    df = pd.read_excel('数字化转型指数合并数据.xlsx')
    st.success("✅ 数据加载成功！")
    
    # 显示数据基本信息
    with st.expander("📋 数据概览"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**数据规模**: {df.shape[0]} 条记录, {df.shape[1]} 个字段")
        with col2:
            st.write(f"**字段名称**: {', '.join(df.columns.tolist())}")
        
        st.write("**数据前3行**:")
        st.dataframe(df.head(3), use_container_width=True)
    
    # 自动检测关键列
    st.header("🔍 自动列检测")
    
    # 检测股票代码列
    code_cols = ['股票代码', '证券代码', '代码', 'stock_code', 'code']
    stock_code_col = None
    for col in code_cols:
        if col in df.columns:
            stock_code_col = col
            break
    
    if not stock_code_col:
        # 如果没有找到预设的代码列名，尝试检测包含数字和字母的列
        for col in df.columns:
            if df[col].dtype == object and df[col].str.match(r'^[A-Z0-9]+$').any():
                stock_code_col = col
                break
    
    # 检测年份列
    year_cols = ['年份', '年度', 'year', 'Year']
    year_col = None
    for col in year_cols:
        if col in df.columns:
            year_col = col
            break
    
    if not year_col:
        # 尝试检测包含年份格式的列
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64'] and df[col].between(2000, 2100).any():
                year_col = col
                break
    
    # 检测数字化转型指数列
    index_cols = ['数字化转型指数', '转型指数', '数字化指数', '指数', 'digital_index', 'index']
    index_col = None
    for col in index_cols:
        if col in df.columns:
            index_col = col
            break
    
    if not index_col:
        # 尝试检测数值列作为指数列
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64'] and col not in [stock_code_col, year_col]:
                index_col = col
                break
    
    # 显示检测结果
    col1, col2, col3 = st.columns(3)
    with col1:
        if stock_code_col:
            st.success(f"✅ 股票代码列: **{stock_code_col}**")
        else:
            st.error("❌ 未检测到股票代码列")
    
    with col2:
        if year_col:
            st.success(f"✅ 年份列: **{year_col}**")
        else:
            st.error("❌ 未检测到年份列")
    
    with col3:
        if index_col:
            st.success(f"✅ 数字化转型指数列: **{index_col}**")
        else:
            st.error("❌ 未检测到数字化转型指数列")
    
    # 如果检测到关键列，进行查询
    if stock_code_col and year_col and index_col:
        st.header("🔎 查询条件")
        
        # 获取唯一的股票代码列表
        stock_codes = sorted(df[stock_code_col].unique().tolist())
        
        # 股票代码选择器
        selected_code = st.selectbox(
            f"选择{stock_code_col}",
            stock_codes,
            index=0
        )
        
        # 获取该股票的所有年份
        years = sorted(df[df[stock_code_col] == selected_code][year_col].unique().tolist())
        
        # 年份选择器
        selected_year = st.selectbox(
            f"选择{year_col}",
            years,
            index=0
        )
        
        # 查询特定股票和年份的数据
        st.header("📈 查询结果")
        
        # 获取查询结果
        result = df[(df[stock_code_col] == selected_code) & (df[year_col] == selected_year)]
        
        if not result.empty:
            # 显示详细数据
            st.subheader(f"{selected_code} - {selected_year}年数据")
            st.dataframe(result, use_container_width=True)
            
            # 显示该年指数值
            index_value = result.iloc[0][index_col]
            st.metric(
                label=f"{selected_year}年数字化转型指数",
                value=round(index_value, 2)
            )
        else:
            st.warning(f"⚠️ 未找到{selected_code}在{selected_year}年的数据")
        
        # 显示该企业历年数字化转型指数折线图
        st.header("📊 历年数字化转型指数趋势")
        
        # 获取该企业的所有数据
        company_data = df[df[stock_code_col] == selected_code]
        
        # 按年份排序
        company_data = company_data.sort_values(year_col)
        
        # 创建折线图
        fig = px.line(
            company_data,
            x=year_col,
            y=index_col,
            title=f"{selected_code}企业历年数字化转型指数趋势",
            labels={
                year_col: "年份",
                index_col: "数字化转型指数"
            },
            markers=True,
            hover_data={
                index_col: ':.2f',
                year_col: True
            }
        )
        
        # 美化图表
        fig.update_layout(
            xaxis_title="年份",
            yaxis_title="数字化转型指数",
            title_x=0.5,
            hovermode="x unified",
            template="plotly_white"
        )
        
        # 显示图表
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示统计信息
        with st.expander("📊 统计信息"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("数据年份范围", f"{company_data[year_col].min()} - {company_data[year_col].max()}")
            with col2:
                st.metric("平均指数", round(company_data[index_col].mean(), 2))
            with col3:
                st.metric("最高指数", round(company_data[index_col].max(), 2))
            with col4:
                st.metric("最低指数", round(company_data[index_col].min(), 2))
    else:
        st.error("❌ 无法识别数据格式，请确保Excel文件包含股票代码、年份和数字化转型指数列")
        st.info("请检查Excel文件结构，确保包含以下关键信息：\n"+
               "- 股票代码（如：600000、AAPL等）\n"+
               "- 年份（如：2020、2021等）\n"+
               "- 数字化转型指数（数值类型）")
        
        # 显示数据结构帮助用户确认
        st.subheader("📋 当前数据结构")
        st.write("列名及数据类型：")
        st.write(df.dtypes.to_frame(name="数据类型"))
        
        # 提供手动映射选项
        st.subheader("🔧 手动列映射（可选）")
        stock_code_col = st.selectbox("选择股票代码列", df.columns.tolist())
        year_col = st.selectbox("选择年份列", df.columns.tolist())
        index_col = st.selectbox("选择数字化转型指数列", df.columns.tolist())
        
        if st.button("应用手动映射"):
            # 重新执行查询逻辑
            st.experimental_rerun()
            
except FileNotFoundError:
    st.error("❌ 文件未找到！")
    st.warning("请确保Excel文件'数字化转型指数合并数据.xlsx'与应用在同一目录下")
except Exception as e:
    st.error(f"❌ 数据加载失败：{str(e)}")
    st.warning("请检查Excel文件格式是否正确，确保为.xlsx格式")

# 页脚
st.markdown("---")
st.markdown("### 📝 注意事项")
st.markdown(
    "1. 确保Excel文件编码正确，避免中文乱码\n"
    "2. 数据中不要包含合并单元格\n"
    "3. 年份建议使用4位数字格式（如：2023）\n"
    "4. 数字化转型指数应为数值类型"
)
