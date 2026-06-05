import streamlit as st
import requests
import json
import datetime
import hmac

# ---------- بخش احراز هویت (قفل پروژه) ----------
def check_password():
    """بررسی رمز عبور برای دسترسی به پروژه"""
    def password_entered():
        if hmac.compare_digest(st.session_state["password"], st.secrets["PASSWORD"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("🔐 رمز عبور پروژه را وارد کنید:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("🔐 رمز عبور اشتباه است! دوباره وارد کنید:", type="password", on_change=password_entered, key="password")
        return False
    return True

# اگر رمز اشتباه بود، برنامه متوقف می‌شود
if not check_password():
    st.stop()
# ---------------------------------------------

st.set_page_config(page_title="تولید کننده سوالات امتحانی و استخدامی", layout="wide")
st.title("📚 سیستم تولید سوالات امتحانی و استخدامی")

# سایدبار تنظیمات
with st.sidebar:
    st.header("⚙️ تنظیمات")
    
    mode = st.radio("حالت:", ["📖 امتحانی", "💼 استخدامی"])
    
    if mode == "📖 امتحانی":
        grade = st.selectbox("پایه تحصیلی", ["دهم", "یازدهم", "دوازدهم"])
        field = st.selectbox("رشته", ["ریاضی", "تجربی", "انسانی", "فنی حرفه‌ای"])
        subject = st.text_input("نام درس", "ریاضی")
        count = st.number_input("تعداد سوال", min_value=1, max_value=100, value=10)
        total_score = st.number_input("بارم کل (نمره)", min_value=1, max_value=100, value=20)
        question_type = st.selectbox("نوع سوال", ["تستی", "تشریحی", "ترکیبی", "جای خالی", "درست/نادرست"])
        difficulty = st.selectbox("سطح دشواری", ["آسان", "متوسط", "سخت", "کنکوری"])
    else:
        topic = st.selectbox("موضوع استخدامی", ["هوش و استعداد تحصیلی", "ریاضی و آمار", "اطلاعات عمومی", "فناوری اطلاعات", "قانون اساسی", "معارف اسلامی", "زبان انگلیسی", "تخصصی رشته"])
        count = st.number_input("تعداد سوال", min_value=1, max_value=500, value=100)
    
    openrouter_key = st.text_input("کلید OpenRouter", type="password", value="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")
    generate_btn = st.button("🚀 تولید سوالات", type="primary", use_container_width=True)

# تولید سوالات
if generate_btn:
    if not openrouter_key:
        st.error("❌ لطفاً کلید OpenRouter را وارد کن")
    else:
        with st.spinner("🤖 در حال تولید سوالات با هوش مصنوعی... (حدود 20-40 ثانیه)"):
            try:
                if mode == "📖 امتحانی":
                    prompt = f"""لطفاً {count} سوال {question_type} از درس {subject} پایه {grade} رشته {field} با بارم کل {total_score} نمره و سطح دشواری {difficulty} طراحی کن.

بعد از هر سوال، پاسخنامه تشریحی کامل بنویس.

فرمت خروجی دقیقاً به این شکل باشد:

**سوال 1:** [متن سوال]
**پاسخ:** [پاسخ صحیح]
**توضیح:** [توضیح کامل تشریحی]

تمام سوالات و پاسخ‌ها به زبان فارسی باشد."""
                else:
                    prompt = f"""لطفاً {count} سوال استخدامی مبحث {topic} با پاسخنامه تشریحی طراحی کن.

فرمت خروجی:

**سوال 1:** [متن سوال]
**پاسخ:** [پاسخ صحیح]
**توضیح:** [توضیح کامل]

تمام سوالات و پاسخ‌ها به زبان فارسی باشد."""
                
                models_to_try = [
                    "openrouter/free",
                    "google/gemma-2-2b-it:free",
                    "qwen/qwen3-next-80b-a3b-instruct:free",
                    "microsoft/phi-3-mini-128k-instruct:free"
                ]
                
                answer = None
                last_error = None
                used_model = None
                
                progress_bar = st.progress(0)
                for idx, model in enumerate(models_to_try):
                    progress_bar.progress((idx + 1) / len(models_to_try))
                    try:
                        response = requests.post(
                            url="https://openrouter.ai/api/v1/chat/completions",
                            headers={
                                "Authorization": f"Bearer {openrouter_key}",
                                "Content-Type": "application/json",
                            },
                            data=json.dumps({
                                "model": model,
                                "messages": [{"role": "user", "content": prompt}],
                                "max_tokens": 4000,
                                "temperature": 0.7
                            }),
                            timeout=90
                        )
                        
                        if response.status_code == 200:
                            answer = response.json()["choices"][0]["message"]["content"]
                            used_model = model
                            break
                        else:
                            last_error = f"{model}: {response.status_code}"
                    except Exception as e:
                        last_error = f"{model}: {str(e)[:50]}"
                
                progress_bar.empty()
                
                if answer:
                    st.success(f"✅ {count} سوال با موفقیت تولید شد!")
                    st.info(f"📌 مدل استفاده شده: {used_model}")
                    st.balloons()
                    
                    st.subheader("📝 سوالات و پاسخنامه")
                    st.markdown("---")
                    st.markdown(answer)
                    st.markdown("---")
                    
                    col1, col2 = st.columns(2)
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    txt_content = f"""تاریخ تولید: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
تعداد سوال: {count}
نوع: {mode}
مدل: {used_model}
---
{answer}
"""
                    
                    with col1:
                        st.download_button("📄 دانلود TXT", txt_content, file_name=f"questions_{timestamp}.txt")
                    with col2:
                        st.download_button("📑 دانلود Word", txt_content.replace("\n", "\r\n"), file_name=f"questions_{timestamp}.docx")
                else:
                    st.error(f"❌ هیچ مدلی کار نکرد. آخرین خطا: {last_error}")
                    
            except Exception as e:
                st.error(f"❌ خطا: {e}")

with st.expander("📖 راهنمای استفاده"):
    st.markdown("""
    - کلید OpenRouter به طور خودکار وارد شده
    - تنظیمات را انتخاب کن
    - روی دکمه تولید سوالات کلیک کن
    """)