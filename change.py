import streamlit as st
import database
import authenticator as auth # For authentication checks, but not for hashing anymore

st.title("⚙️ 账户管理")

# --- Authentication Check ---
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    auth.show_login_page()
    st.stop()

current_username = st.session_state.get('username')
current_user = database.get_user_by_username(current_username)
current_user_id = current_user['id'] if current_user else None

if not current_user_id:
    st.error("无法获取当前用户信息，请尝试重新登录。")
    st.stop()

is_admin = (current_username == "admin")

st.info(f"当前用户: **{current_username}** {'(管理员)' if is_admin else '(普通用户)'}")

# --- Common Password Change Logic ---
def password_change_form(target_user_id, target_username, form_title="修改密码"):
    st.subheader(form_title)
    with st.form(key=f"change_password_form_{target_user_id}"):
        new_password = st.text_input("新密码:", type="password", key=f"new_pw_{target_user_id}")
        confirm_password = st.text_input("确认新密码:", type="password", key=f"confirm_pw_{target_user_id}")
        submit_button = st.form_submit_button("提交修改")

        if submit_button:
            if not new_password or not confirm_password:
                st.warning("密码和确认密码都不能为空。")
            elif new_password != confirm_password:
                st.error("新密码和确认密码不匹配。")
            else:
                # Store plain text password as requested
                # Removed: hashed_password = auth.hash_password(new_password)
                if database.update_user_password(target_user_id, new_password): # Pass plain text password
                    st.success(f"用户 '{target_username}' 的密码已成功修改！")
                    if target_user_id == current_user_id: # If current user changed their own password
                        st.warning("您的密码已更改，请记住新密码。")
                else:
                    st.error("修改密码失败，请稍后再试。")

# --- UI for Admin User ---
if is_admin:
    st.header("管理员操作")

    # Display all users for selection
    all_users = database.get_all_users()
    # Exclude admin from modification/deletion in the admin UI itself
    # If 'admin' user is chosen, it means admin wants to modify their own account,
    # which is handled in the 'My Account Management' section below.
    user_options = {f"{user['username']} (ID: {user['id']})": user['id'] for user in all_users if user['username'] != "admin"}

    if not user_options:
        st.info("没有其他用户可供管理。")
    else:
        selected_user_display = st.selectbox(
            "选择要操作的用户:",
            options=list(user_options.keys()),
            key="admin_user_select"
        )

        selected_user_id_for_admin = user_options.get(selected_user_display)
        # Extract username from display string like "username (ID: 1)"
        selected_username_for_admin = selected_user_display.split(' ')[0]

        if selected_user_id_for_admin:
            st.markdown(f"---")
            st.subheader(f"操作用户: **{selected_username_for_admin}**")

            # Admin: Change password for selected user
            password_change_form(selected_user_id_for_admin, selected_username_for_admin, form_title=f"修改 '{selected_username_for_admin}' 的密码")

            st.markdown(f"---")
            # Admin: Delete user
            st.subheader(f"删除用户 '{selected_username_for_admin}'")
            if st.button(f"删除用户 '{selected_username_for_admin}'", key="delete_user_button", type="secondary"):
                if st.warning(f"确定要删除用户 '{selected_username_for_admin}' 及其所有数据吗？此操作不可逆！"): # Confirm deletion
                    if database.delete_user(selected_user_id_for_admin):
                        st.success(f"用户 '{selected_username_for_admin}' 已成功删除！")
                        st.experimental_rerun() # Rerun to refresh user list
                    else:
                        st.error("删除用户失败，请稍后再试。")
                else:
                    st.info("删除操作已取消。")
        else:
            st.warning("请选择一个用户进行管理操作。")


# --- UI for Regular User (or Admin's own account management) ---
if not is_admin:
    st.header("个人账户管理")
    password_change_form(current_user_id, current_username, form_title="修改我的密码")
else: # Admin can also change their own password if desired, separately from admin operations
    st.markdown("---")
    st.header("我的账户管理")
    password_change_form(current_user_id, current_username, form_title="修改我的管理员密码")