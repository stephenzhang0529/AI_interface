import streamlit as st

#profiles
st.write("#### Hi! I am _StephenZhang_ :panda_face:")
st.markdown(
    """
    ## An undergraduate at <a href="https://www.neu.edu.cn/" style="color:#1f77b4; text-decoration:none;"><strong>NEU</strong></a>, majoring in CS
    """,
    unsafe_allow_html=True
)
st.write("I'm passionate about artificial intelligence, especially RL and Embodied Intelligence...")



st.divider()
#contact
st.write("Contact Me:")
col1,col2=st.columns(2)
with col1:
  st.link_button("Go to My GitHub:computer:","https://github.com/stephenzhang0529")
with col2:
  st.link_button("Email Me:email:","mailto:stephenzhang0529@gmail.com")
st.divider()