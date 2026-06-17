import streamlit as st
import requests
import json
import datetime

st.set_page_config(page_title="تولید کننده سوالات امتحانی و استخدامی", layout="wide")
st.title("📚 سیستم تولید سوالات امتحانی و استخدامی")

# ====== تنظیمات AvalAI ======
AVALAI_API_KEY = "aa-s5Ebh8oQHNjI4skZYIEsdsqStBtJLDAIt9RMAcp0yTxJ083Z"  # ⚠️ کلید جدید خود را اینجا قرار دهید
AVALAI_BASE_URL = "https://api.avalai.ir/v1"
# ============================

with st.sidebar:
    st.header("⚙️ تنظیمات")
    
    mode = st.radio("حالت:", ["📖 امتحانی", "💼 استخدامی"])
    
    if mode == "📖 امتحانی":
        grade = st.selectbox("پایه تحصیلی", ["دهم", "یازدهم", "دوازدهم"])
        field = st.selectbox("رشته", ["ریاضی", "تجربی", "انسانی"])
        subject = st.text_input("نام درس", "ریاضی")
        count = st.number_input("تعداد سوال", 1, 50, 5)
        total_score = st.number_input("بارم کل (نمره)", 1, 100, 20)
        question_type = st.selectbox("نوع سوال", ["تستی", "تشریحی", "ترکیبی", "درست/نادرست"])
        difficulty = st.selectbox("سطح دشواری", ["آسان", "متوسط", "سخت"])
    else:
        topic = st.selectbox("موضوع استخدامی", ["هوش", "اطلاعات عمومی", "معارف", "زبان انگلیسی", "تخصصی"])
        count = st.number_input("تعداد سوال", 1, 200, 50)
    
    generate_btn = st.button("🚀 تولید سوالات", type="primary")

if generate_btn:
    if not AVALAI_API_KEY or AVALAI_API_KEY == "YOUR_AVALAI_API_KEY":
        st.error("❌ لطفاً کلید API معتبر را در کد وارد کنید.")
    else:
        with st.spinner("🤖 در حال تولید سوالات... (حدود 20-40 ثانیه)"):
            try:
                if mode == "📖 امتحانی":
                    prompt = f"""لطفاً {count} سوال {question_type} از درس {subject} پایه {grade} رشته {field} با بارم کل {total_score} نمره و سطح دشواری {difficulty} طراحی کن.

بعد از هر سوال، پاسخنامه تشریحی کامل بنویس.

فرمت خروجی:
سوال 1: [متن سوال]
پاسخ: [پاسخ صحیح]
توضیح: [توضیح کامل]

تمام سوالات و پاسخ‌ها به زبان فارسی باشد."""
                else:
                    prompt = f"""لطفاً {count} سوال استخدامی مبحث {topic} با پاسخنامه تشریحی طراحی کن.

فرمت خروجی:
سوال 1: [متن سوال]
پاسخ: [پاسخ صحیح]
توضیح: [توضیح کامل]

تمام سوالات و پاسخ‌ها به زبان فارسی باشد."""

                # استفاده از AvalAI به جای OpenRouter
                response = requests.post(
                    url=f"{AVALAI_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {AVALAI_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "gemini-3.5-flash",  # یا هر مدل دیگری که در AvalAI فعال است
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 3000,
                        "temperature": 0.7
                    },
                    timeout=90
                )

                if response.status_code == 200:
                    answer = response.json()["choices"][0]["message"]["content"]
                    
                    st.success(f"✅ {count} سوال با موفقیت تولید شد!")
                    st.balloons()
                    
                    st.subheader("📝 سوالات و پاسخنامه")
                    st.markdown("---")
                    st.markdown(answer)
                    st.markdown("---")
                    
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.download_button("📥 دانلود سوالات", answer, file_name=f"questions_{timestamp}.txt")
                else:
                    st.error(f"❌ خطا در ارتباط با AvalAI: {response.status_code}")
                    st.info("💡 راهنمایی: مطمئن شوید کلید API معتبر است و مدل انتخاب شده در AvalAI فعال است.")
                    
            except Exception as e:
                st.error(f"❌ خطا: {e}")

with st.expander("📖 راهنمای استفاده"):
    st.markdown("""
    - کلید AvalAI را در کد وارد کنید.
    - تنظیمات مورد نظر را انتخاب کنید.
    - روی دکمه تولید سوالات کلیک کنید.
    
    **مدل‌های پشتیبانی‌شده در AvalAI:** Gemini 3.5 Flash، DeepSeek V4 Pro، Grok 4.3 و ...
    """)
