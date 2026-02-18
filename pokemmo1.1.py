import streamlit as st
from collections import defaultdict

# 1. 页面基本配置
st.set_page_config(page_title="Pokemmo 孵蛋 1.0", layout="wide")

# 2. 注入自定义 CSS 样式 (完全沿用 1.0 存档版)
st.markdown("""
    <style>
    /* 全局字体 */
    html, body, [class*="css"] {
        font-family: "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    }
    
    /* --- 隐藏顶部开发者栏 --- */
    header[data-testid="stHeader"] {
        display: none;
    }
    /* 调整一下顶部间距，防止内容被切掉 */
    .block-container {
        padding-top: 2rem !important; 
    }
    
    /* 阶段标题 */
    .stage-title {
        background-color: #3F51B5;
        color: white;
        padding: 12px 15px;
        font-size: 20px;
        font-weight: bold;
        border-radius: 6px; /* 统一圆角 */
        margin: 25px 0 10px 0;
    }
    
    /* 任务组标题 */
    .task-header {
        background-color: #E8EAF6;
        color: #1A237E;
        padding: 10px 15px;
        font-weight: bold;
        margin: 15px 0 5px 0;
        border-left: 5px solid #3F51B5;
        border-radius: 6px; /* 统一圆角 */
    }
    
    /* 恭喜标题 */
    .congrats-title {
        background-color: #D32F2F;
        color: #FFD700;
        padding: 12px 15px;
        font-size: 20px;
        font-weight: bold;
        border-radius: 6px; /* 统一圆角 */
        margin: 25px 0;
    }

    /* --- 通用信息块样式 (统一背景与圆角) --- */
    .info-box {
        padding: 6px 12px;
        margin-bottom: 6px;
        border-radius: 6px; /* 统一所有框的圆角 */
        font-size: 15px;
        line-height: 1.6;
    }
    
    /* 各类别的配色 */
    .bg-recipe { background-color: #E3F2FD; color: #0D47A1; border-left: 4px solid #2196F3; } /* 配方-蓝 */
    .bg-lock   { background-color: #FFF3E0; color: #E65100; border-left: 4px solid #FF9800; } /* 锁项-橙 (已去粗) */
    .bg-stat   { background-color: #F3E5F5; color: #4A148C; border-left: 4px solid #9C27B0; } /* 统计-紫 */
    .bg-mat    { background-color: #FAFAFA; color: #424242; border-left: 4px solid #9E9E9E; } /* 素材-灰 */
    .bg-warn   { background-color: #FFEBEE; color: #C62828; font-weight: bold; border-left: 4px solid #F44336; } /* 警告-红 */
    .bg-strat  { background-color: #E8F5E9; color: #1B5E20; font-weight: bold; border-left: 4px solid #4CAF50; } /* 策略-绿 */
    .bg-tip    { background-color: #E1F5FE; color: #0277BD; font-weight: bold; border-left: 4px solid #03A9F4; } /* 提示-青 */
    .bg-overlap{ background-color: #E0F2F1; color: #00695C; font-weight: bold; border-left: 4px solid #009688; } /* 重叠-深青 */

    /* 适配手机端屏幕 */
    @media (max-width: 640px) {
        .content-box { padding-left: 15px; font-size: 14px; }
        .stage-title, .congrats-title { font-size: 16px; }
    }
    
    /* 配置区小标题样式 */
    .config-label {
        font-size: 14px;
        font-weight: bold;
        color: rgb(49, 51, 63);
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 性格数据
natures = [
    "不锁性格 (随机修正)",
    "固执 (+攻击 -特攻)", "开朗 (+速度 -特攻)", "保守 (+特攻 -攻击)", 
    "胆小 (+速度 -攻击)", "勇敢 (+攻击 -速度)", "冷静 (+特攻 -速度)",
    "大胆 (+防御 -攻击)", "淘气 (+防御 -特攻)", "悠闲 (+防御 -速度)",
    "温和 (+特防 -攻击)", "慎重 (+特防 -特攻)", "狂妄 (+特防 -速度)",
    "顽皮 (+攻击 -特防)", "马虎 (+特攻 -特防)", "天真 (+速度 -特防)",
    "孤独 (+攻击 -防御)", "稳重 (+特攻 -防御)", "急躁 (+速度 -防御)",
    "乐天 (+防御 -特防)", "温顺 (+特防 -防御)",
    "大体 (不变修正)", "认真 (不变修正)", "努力 (不变修正)", "羞涩 (不变修正)", "坦率 (不变修正)"
]

def get_pascals_coeffs(n):
    line = [1]
    for k in range(n): line.append(line[k] * (n - k) // (k + 1))
    return line

# --- 网页交互界面 ---
st.title("Pokemmo 孵蛋大师 1.1")

# 配置区 (完全沿用 1.0 代码，不做任何改动)
with st.expander("配置", expanded=True):
    # 添加“目标属性”小标题
    st.markdown('<div class="config-label">目标属性</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    stats = ["生命", "攻击", "防御", "特攻", "特防", "速度"]
    stat_selection = {}
    
    for i, stat in enumerate(stats):
        target_col = [col1, col2, col3][i % 3]
        with target_col:
            c1, c2 = st.columns([1, 1])
            is_on = c1.checkbox(stat, key=f"s_{stat}")
            weight = c2.number_input("权重", min_value=1, value=1, key=f"w_{stat}", label_visibility="collapsed")
            stat_selection[stat] = {"on": is_on, "weight": weight}

    # 目标性格
    st.markdown('<div class="config-label" style="margin-top: 10px;">目标性格</div>', unsafe_allow_html=True)
    target_nature = st.selectbox("目标性格", natures, label_visibility="collapsed")

# --- 双按钮布局 ---
c_btn1, c_btn2 = st.columns(2)
with c_btn1:
    btn_normal = st.button("生成孵蛋方案", type="primary", use_container_width=True)
with c_btn2:
    btn_genderless = st.button("生成无性别孵蛋方案", type="primary", use_container_width=True)

# --- 核心逻辑函数 ---
def prepare_data():
    selected_stats = [{"name": s, "prop": s, "weight": info["weight"]} for s, info in stat_selection.items() if info["on"]]
    has_nature = "不锁性格" not in target_nature
    total_items = len(selected_stats) + (1 if has_nature else 0)
    return selected_stats, has_nature, total_items

def build_slots(total_items, has_nature, selected_stats):
    coeffs = get_pascals_coeffs(total_items - 1)
    slots = [{"index": i, "count": count, "assigned": None} for i, count in enumerate(coeffs)]
    if has_nature:
        slots[0]["assigned"] = {"name": target_nature.split(" ")[0], "prop": "性格", "weight": 999}
    
    available_slots = sorted([s for s in slots if s["assigned"] is None], key=lambda x: x["count"], reverse=True)
    selected_stats.sort(key=lambda x: x["weight"])
    for i, slot in enumerate(available_slots):
        slot["assigned"] = selected_stats[i]
    
    slots.sort(key=lambda x: x["index"])
    return [s["assigned"] for s in slots]

def build_tree_structure(traits, start, end):
    if start == end: 
        return {"type": "leaf", "level": 1, "node_name": traits[start]['name'], "traits_set": {traits[start]['name']}}
    l, r = build_tree_structure(traits, start, end - 1), build_tree_structure(traits, start + 1, end)
    all_n = [t['name'] for t in traits[start:end+1]]
    return {"type": "node", "left": l, "right": r, "level": len(all_n), "res_name": "+".join(all_n), "node_name": "+".join(all_n), "l_lock": traits[start]['prop'], "r_lock": traits[end]['prop'], "traits_set": set(all_n)}

# --- 逻辑 A: 正常孵蛋 (1.0 原版逻辑) ---
if btn_normal:
    selected_stats, has_nature, total_items = prepare_data()
    if total_items < 2:
        st.error("错误：请至少选择两个目标（如两个属性，或一个属性加性格）")
    else:
        final_list = build_slots(total_items, has_nature, selected_stats)
        root = build_tree_structure(final_list, 0, len(final_list)-1)

        def calc_gender(node):
            if node['type'] == 'leaf': return
            node['left']['gender_req'], node['right']['gender_req'] = "母", "公"
            calc_gender(node['left']); calc_gender(node['right'])

        root['gender_req'] = "任意"
        calc_gender(root)

        # 阶段 0
        st.markdown('<div class="stage-title">■ 阶段 0 >>> 1 </div>', unsafe_allow_html=True)
        stats_count = defaultdict(lambda: {'母': 0, '公': 0})
        def scan_mats(n):
            if n['type'] == 'leaf' and n.get('gender_req', '任意') != '任意':
                stats_count[n['node_name']][n['gender_req']] += 1
            elif n['type'] != 'leaf': scan_mats(n['left']); scan_mats(n['right'])
        scan_mats(root)
        
        mat_html = '<div>'
        for i, t in enumerate(final_list):
            n = t['name']; f, m = stats_count[n]['母'], stats_count[n]['公']
            mat_html += f'<div class="info-box bg-mat">{n} (权重:{t["weight"]}) | 总需: {f+m} | 详情: {f}母 + {m}公</div>'
        mat_html += f'<div class="info-box bg-warn" style="margin-top:10px;">合计素材: {sum(s["母"]+s["公"] for s in stats_count.values())} 只</div></div>'
        st.markdown(mat_html, unsafe_allow_html=True)

        # 合成阶段
        all_steps = []
        def collect(n):
            if n['type'] != 'leaf': collect(n['left']); collect(n['right']); all_steps.append(n)
        collect(root)
        all_steps.sort(key=lambda x: x['level'])
        
        grouped = defaultdict(list)
        for s in all_steps: grouped[(s['level'], s['res_name'])].append(s)
        
        current_lvl = 0
        sorted_keys = sorted(grouped.keys(), key=lambda x: x[0])
        for i, (lvl, name) in enumerate(sorted_keys):
            is_final = (i == len(sorted_keys) - 1)
            steps_in_group = grouped[(lvl, name)]
            if lvl > current_lvl:
                current_lvl = lvl
                st.markdown(f'<div class="stage-title">■ 阶段 {current_lvl-1} >>> {current_lvl}</div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="task-header">■ 任务组: 制作 {len(steps_in_group)} 个 [{name}]</div>' if not is_final else f'<div class="task-header">■ 任务组: 制作最终成品 [{name}]</div>', unsafe_allow_html=True)
            
            step = steps_in_group[0]
            l_nm = ("1V " if step['left']['type']=='leaf' else "") + step['left']['node_name']
            r_nm = ("1V " if step['right']['type']=='leaf' else "") + step['right']['node_name']
            
            count = len(steps_in_group)
            req_f = sum(1 for s in steps_in_group if "母" in s.get('gender_req', ''))
            req_m = sum(1 for s in steps_in_group if "公" in s.get('gender_req', ''))

            res_html = f'<div class="info-box bg-recipe">【配方】 [母] {l_nm} | [公] {r_nm}</div>'
            res_html += f'<div class="info-box bg-lock">【锁项】 母锁[{step["l_lock"]}] | 父锁[{step["r_lock"]}]</div>'
            
            overlap = step['left']['traits_set'].intersection(step['right']['traits_set'])
            if overlap: res_html += f'<div class="info-box bg-overlap">【重叠】 共享属性: {"+".join(list(overlap))} (必须均为31)</div>'
            
            if not is_final:
                res_html += f'<div class="info-box bg-stat">【统计】 目标性别: 需 {req_f}母 + {req_m}公</div>'
                if "性格" in str(step['l_lock']) or "性格" in str(step['r_lock']):
                    res_html += f'<div class="info-box bg-warn">【警告】 涉及性格遗传，严禁博弈！请锁{"母" if req_f else "公"}！</div>'
                elif count >= 2:
                    limit = count - max(req_f, req_m)
                    if limit > 0:
                        res_html += f'<div class="info-box bg-strat">【策略】 省钱博弈(容错 {limit} 对)：先拿 {limit} 对不锁性别赌，剩下补齐。</div>'
            else:
                if total_items < 7:
                    res_html += f'<div class="info-box bg-tip">【追梦提示】 成品推荐锁 ♀(母)，方便后续追梦高V。</div>'
                st.markdown(res_html, unsafe_allow_html=True)
                st.markdown(f'<div class="congrats-title">恭喜制作成功！祝你的宝可梦在赛场上大放异彩！</div>', unsafe_allow_html=True)
                continue
            
            st.markdown(res_html, unsafe_allow_html=True)

# --- 逻辑 B: 无性别孵蛋 (新逻辑) ---
if btn_genderless:
    selected_stats, has_nature, total_items = prepare_data()
    if total_items < 2:
        st.error("错误：请至少选择两个目标（如两个属性，或一个属性加性格）")
    else:
        final_list = build_slots(total_items, has_nature, selected_stats)
        root = build_tree_structure(final_list, 0, len(final_list)-1)
        
        # 无性别渲染
        st.markdown('<div class="stage-title">■ 阶段 0 >>> 1</div>', unsafe_allow_html=True)
        
        stats_count = defaultdict(int)
        def scan_mats_no_gender(n):
            if n['type'] == 'leaf':
                stats_count[n['node_name']] += 1
            else:
                scan_mats_no_gender(n['left'])
                scan_mats_no_gender(n['right'])
        scan_mats_no_gender(root)
        
        mat_html = '<div>'
        for i, t in enumerate(final_list):
            n = t['name']
            c = stats_count[n]
            # 无性别专属文案
            mat_html += f'<div class="info-box bg-mat">{n} (权重:{t["weight"]}) | 总需: {c} | 详情: {c} 百变怪 | 本进化链</div>'
        mat_html += f'<div class="info-box bg-warn" style="margin-top:10px;">合计素材: {sum(stats_count.values())} 只</div></div>'
        st.markdown(mat_html, unsafe_allow_html=True)

        all_steps = []
        def collect(n):
            if n['type'] != 'leaf': collect(n['left']); collect(n['right']); all_steps.append(n)
        collect(root)
        all_steps.sort(key=lambda x: x['level'])
        
        grouped = defaultdict(list)
        for s in all_steps: grouped[(s['level'], s['res_name'])].append(s)
        
        current_lvl = 0
        sorted_keys = sorted(grouped.keys(), key=lambda x: x[0])
        for i, (lvl, name) in enumerate(sorted_keys):
            is_final = (i == len(sorted_keys) - 1)
            steps_in_group = grouped[(lvl, name)]
            if lvl > current_lvl:
                current_lvl = lvl
                st.markdown(f'<div class="stage-title">■ 阶段 {current_lvl-1} >>> {current_lvl}</div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="task-header">■ 任务组: 制作 {len(steps_in_group)} 个 [{name}]</div>' if not is_final else f'<div class="task-header">■ 任务组: 制作最终成品 [{name}]</div>', unsafe_allow_html=True)
            
            step = steps_in_group[0]
            l_nm = ("1V " if step['left']['type']=='leaf' else "") + step['left']['node_name']
            r_nm = ("1V " if step['right']['type']=='leaf' else "") + step['right']['node_name']
            
            # 无性别专属：去掉了公母标签，修改了锁项文案
            res_html = f'<div class="info-box bg-recipe">【配方】 {l_nm} | {r_nm}</div>'
            res_html += f'<div class="info-box bg-lock">【锁项】 左锁[{step["l_lock"]}] | 右锁[{step["r_lock"]}]</div>'
            
            overlap = step['left']['traits_set'].intersection(step['right']['traits_set'])
            if overlap: res_html += f'<div class="info-box bg-overlap">【重叠】 共享属性: {"+".join(list(overlap))} (必须均为31)</div>'
            
            # 移除了统计栏和策略栏
            if not is_final:
                if "性格" in str(step['l_lock']) or "性格" in str(step['r_lock']):
                    res_html += f'<div class="info-box bg-warn">【警告】 涉及性格遗传，严禁博弈！请检查！</div>'
            else:
                if total_items < 7:
                    res_html += f'<div class="info-box bg-tip">【追梦提示】 成品推荐锁 ♀(母)，方便后续追梦高V。</div>'
                st.markdown(res_html, unsafe_allow_html=True)
                st.markdown(f'<div class="congrats-title">恭喜制作成功！祝你的宝可梦在赛场上大放异彩！</div>', unsafe_allow_html=True)
                continue
            
            st.markdown(res_html, unsafe_allow_html=True)