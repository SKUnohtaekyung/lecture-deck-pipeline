from playwright.sync_api import sync_playwright
U='http://localhost:8810/tmp/frame/view/live_deck.html'
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1280,'height':720}); pg.goto(U+'?audit'); pg.wait_for_timeout(900)
    order=pg.evaluate("[...document.querySelectorAll('section.slide')].map(s=>s.dataset.slide)")
    q=b.new_page(viewport={'width':1280,'height':720}); q.goto(f"{U}?audit#slide={order.index('M2-2')+1}"); q.wait_for_timeout(900)
    print(q.evaluate("""(()=>{const s=document.querySelector('section[data-slide="M2-2"]');const c=s.querySelector('.terminal-copy');const r=s.getBoundingClientRect();
    let worst=0;s.querySelectorAll('*').forEach(e=>{const b=e.getBoundingClientRect();if(b.height>0)worst=Math.max(worst,b.bottom-r.bottom)});
    return {sh:c.scrollHeight,ch:c.clientHeight,overBottom:Math.round(worst),fs:getComputedStyle(c.querySelector('p')).fontSize}})()"""))
    q.screenshot(path='tmp/frame/E/shots/_main_M2-2.png'); b.close()
