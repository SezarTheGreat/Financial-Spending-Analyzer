import sys
sys.stdout.reconfigure(encoding='utf-8')
import re

def formatChatMarkdown(raw):
    if not raw:
        return ''
    text = raw.strip()
    
    # 1. Extract Display Math
    mathBlocks = []
    def math_sub(m):
        formula = m.group(1)
        placeholder = f"___MATH_BLOCK_{len(mathBlocks)}___"
        mathBlocks.append(f'<div class="formula-env-card"><div class="formula-env-body">$${formula.strip()}$$</div></div>')
        return f"\n\n{placeholder}\n\n"
    text = re.sub(r'\$\$([\s\S]*?)\$\$', math_sub, text)
    
    # 7. Parse line-by-line for ordered and unordered lists
    lines = text.split('\n')
    out = []
    inUl = False
    inOl = False
    
    for i in range(len(lines)):
        line = lines[i]
        trim = line.strip()
        if not trim:
            if inUl: out.append('</ul>'); inUl = False
            if inOl: out.append('</ol>'); inOl = False
            continue
        
        olMatch = re.match(r'^(\d+)\.\s+(.*)$', trim)
        subUlMatch = re.match(r'^\s{2,}[-*]\s+(.*)$', line)
        ulMatch = re.match(r'^[-*]\s+(.*)$', trim)
        
        if subUlMatch and inOl:
            out.append(f'<ul style="margin:4px 0 8px 18px; padding-left:14px; list-style-type:disc;"><li>{subUlMatch.group(1)}</li></ul>')
        elif olMatch:
            if inUl: out.append('</ul>'); inUl = False
            if not inOl: out.append('<ol style="margin:8px 0; padding-left:22px;">'); inOl = True
            out.append(f'<li value="{olMatch.group(1)}" style="margin-bottom:6px;">{olMatch.group(2)}</li>')
        elif ulMatch:
            if inOl: out.append('</ol>'); inOl = False
            if not inUl: out.append('<ul style="margin:8px 0; padding-left:20px; list-style-type:disc;">'); inUl = True
            out.append(f'<li style="margin-bottom:4px;">{ulMatch.group(1)}</li>')
        else:
            if inUl: out.append('</ul>'); inUl = False
            if inOl: out.append('</ol>'); inOl = False
            out.append(f'<p>{trim}</p>')
    
    if inUl: out.append('</ul>')
    if inOl: out.append('</ol>')
    html = '\n'.join(out)
    for idx, block in enumerate(mathBlocks):
        html = html.replace(f"___MATH_BLOCK_{idx}___", block)
    return html

sample_md = """1. Phase 1 (Days 1–7): Asset Allocation Realignment
   - Current Finding: Equity exposure is 37.89% vs target corridor
   - Action: Redirect incremental monthly SIP cash flows
2. Phase 2 (Days 8–15): Direct Plan Verification
   - Action: Ensure automated SIP mandates remain Direct-Growth
3. Phase 3 (Days 16–30): Quarterly Drift Monitoring
   - Action: Set a quarterly calendar review"""

html = formatChatMarkdown(sample_md)
print("Generated HTML:")
print(html)
assert '<li value="1"' in html
assert '<li value="2"' in html
assert '<li value="3"' in html
assert '<li>Current Finding: Equity exposure is 37.89% vs target corridor</li>' in html
assert '<li>Action: Ensure automated SIP mandates remain Direct-Growth</li>' in html
print("Ordered list test PASSED with continuous values 1, 2, 3 and nested sub-bullets!")
