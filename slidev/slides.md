---
theme: default
title: 舍友心晴
info: |
  舍友心晴——大学生宿舍压力预警与沟通演练助手
class: pop-deck
drawings:
  persist: false
transition: slide-left
duration: 3min
canvasWidth: 980
aspectRatio: 16/9
---

<CoverSlide />

<!--
时间：15 秒
开场只讲一句：这是一个把宿舍压力记录、分析、演练和复盘串成闭环的沟通辅助工具。
-->

---
class: pain-slide
---

<PainSlide />

<!--
时间：25 秒
这里讲痛点，不展开案例细节。
-->

---
class: product-loop-slide
clicks: 7
---

<ProductLoopSlide />

<!--
时间：35 秒
强调闭环即可，先不讲字段、算法和页面细节。
-->

---

# 演示视频

<div class="demo-layout mt-6">
  <div class="video-shell">
    <div class="video-title">50 秒完整流程视频占位</div>
    <div class="video-grid">
      <div>压力分析</div>
      <div>场景训练</div>
      <div>AI 多轮对话</div>
      <div>复盘报告</div>
    </div>
  </div>

  <AnalysisComponentPreview />
</div>

<div class="demo-timing mt-4">记录入口 5s → 压力分析 15s → 场景训练 10s → AI 演练 15s → 复盘报告 5s</div>

<!--
时间：50 秒
后续把视频文件放进 public 或用远程链接替换这里的占位区。
-->

---
class: architecture-slide
---

<ArchitectureSlide />

<!--
时间：35 秒
只讲四层职责，不进入接口列表。
-->

---
class: ai-service-slide
---

<AIServiceSlide />

<!--
时间：30 秒
AI 服务层的核心是多角色编排。用户发送一句话后，系统不是直接生成整段聊天，而是先读取会话记忆，再由 Speaker Planner 判断本轮哪些舍友发言以及顺序。随后系统按顺序逐个调用单舍友生成器，每个后发言的舍友都能看到历史对话和本轮前序回复，因此可以形成反驳、补充、调和和再次发言。最后结果经过结构化校验，写入会话记忆，并用于后续复盘。
-->

---
class: thanks-slide
---

<ThanksSlide />

<!--
以上就是我们的作品展示，感谢各位老师聆听，欢迎提问。
-->
