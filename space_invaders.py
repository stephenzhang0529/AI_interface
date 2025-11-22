import streamlit as st
import json
import os
import database # Import your database module

# --- Placeholder for User Login (In a real app, this would come from an actual login) ---
if 'user_id' not in st.session_state:
    st.session_state.user_id = 1 # Default to a user ID for testing. You might want to register a user first.
    st.session_state.username = "GuestPlayer" # Default username for testing

# To make the leaderboard functional, ensure user_id and username are set after login.
# Example:
# if st.session_state.get('logged_in_user'):
#     st.session_state.user_id = st.session_state.logged_in_user['id']
#     st.session_state.username = st.session_state.logged_in_user['username']
# else:
#     st.session_state.user_id = None # Or redirect to login page
#     st.session_state.username = None


# Set page configuration
st.set_page_config(page_title="Space Invaders", layout="wide", initial_sidebar_state="expanded")

# --- Game State Management ---
if 'game_active' not in st.session_state:
    st.session_state.game_active = False
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'lives' not in st.session_state:
    st.session_state.lives = 3
# High score is now handled by the database for the current user (if logged in) or globally for the game type
# Removed 'high_score' from session_state as it's fetched from DB or calculated

# --- Sidebar ---
with st.sidebar:
    st.title("🚀 Space Invaders 🚀")
    st.markdown("---")

    if st.session_state.user_id:
        st.write(f"欢迎, **{st.session_state.username}**!")
    else:
        st.warning("请登录以保存您的分数并查看排行榜。")

    with st.expander("游戏说明 (Instructions)", expanded=False):
        st.markdown("""
            ### 游戏规则：
            - 使用键盘的左右箭头键 (或 A/D 键) 移动你的飞船。
            - 使用空格键发射子弹。
            - 击中外星人获得分数。
            - 避免被外星人击中或让外星人到达你的防线。
            - 每消灭一波外星人，下一波移动速度会增加，你的得分奖励也会增加。

            ### 控制 (Controls)：
            - **← / A** : 向左移动 (Move Left)
            - **→ / D** : 向右移动 (Move Right)
            - **空格键 (Spacebar)** : 发射子弹 (Shoot)
            - **Enter (游戏结束后)**: 在游戏画面内重新开始 (Restart game within canvas after Game Over)

            *提示: 点击游戏区域以确保键盘输入被捕获。*
            """)
    st.markdown("---")

    st.subheader("📊 游戏状态 (Game Status)")
    col1_metric, col2_metric = st.columns(2)
    with col1_metric:
        st.metric("分数", st.session_state.score)
    with col2_metric:
        st.metric("生命", "❤️" * st.session_state.lives if st.session_state.lives > 0 else "💔")

    st.markdown("---")

    if not st.session_state.game_active:
        if st.button("开始游戏 (Start Game)", key="start_game_button", type="primary", use_container_width=True):
            if st.session_state.user_id: # Only allow starting if a user is identified
                st.session_state.game_active = True
                st.session_state.score = 0
                st.session_state.lives = 3
                if "game_component_data" in st.session_state:
                    del st.session_state.game_component_data
                st.rerun()
            else:
                st.warning("请先登录才能开始游戏！")
    else:
        if st.button("结束游戏 (End Game)", key="end_game_button", type="secondary", use_container_width=True):
            st.session_state.game_active = False
            # Save score when game ends
            if st.session_state.user_id:
                database.save_game_score(st.session_state.user_id, "Space Invaders", st.session_state.score)
                st.toast(f"分数 {st.session_state.score} 已保存!", icon="💾")
            st.rerun()

    st.markdown("---")
    st.subheader("🏆 排行榜 (Leaderboard)")
    if st.session_state.user_id:
        leaderboard_data = database.get_leaderboard("Space Invaders", limit=5)
        if leaderboard_data:
            for i, entry in enumerate(leaderboard_data):
                st.write(f"**{i+1}. {entry['username']}** - {entry['score']}")
        else:
            st.info("还没有分数。成为第一个！")
    else:
        st.info("登录后查看排行榜。")


# --- Main Game Area ---
game_column = st.container()

with game_column:
    if st.session_state.game_active:
        initial_score_py = st.session_state.score
        initial_lives_py = st.session_state.lives

        game_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Space Invaders Canvas</title>
            <style>
                body {{ /* Apply to iframe body */
                    overflow: hidden;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    background-color: #333; /* Dark background for iframe if canvas doesn't fill */
                    min-height: 100vh;
                }}
                #gameCanvas {{
                    border: 2px solid #6c757d;
                    background-color: black;
                    display: block; /* Remove extra space below canvas */
                    /* margin: 10px auto; Removed margin to let flexbox center */
                    touch-action: none;
                }}
            </style>
        </head>
        <body>
            <canvas id="gameCanvas" width="800" height="600"></canvas>
            <script>
                const canvas = document.getElementById('gameCanvas');
                const ctx = canvas.getContext('2d');

                let score = {initial_score_py};
                let lives = {initial_lives_py};
                let gameOver = false;
                let gameOverSentToPython = false; // Flag to send game over state only once

                function sendDataToStreamlit(data) {{
                    if (window.parent && window.parent.streamlit) {{
                        window.parent.streamlit.setComponentValue(JSON.stringify(data));
                    }} else {{
                        console.warn("Streamlit communication layer not found.");
                    }}
                }}

                const player = {{
                    x: canvas.width / 2 - 25,
                    y: canvas.height - 70,
                    width: 50,
                    height: 30,
                    speed: 8,
                    color: '#28a745',
                    isMovingLeft: false,
                    isMovingRight: false,
                    shootCooldown: 0,
                    shootCooldownMax: 12 // Slightly slower fire rate
                }};

                let bullets = [];
                const bulletSpeed = 9;
                const bulletWidth = 4;
                const bulletHeight = 12;

                let aliens = [];
                const alienRowsDefault = 4;
                const alienColsDefault = 8;
                let alienRows = alienRowsDefault;
                let alienCols = alienColsDefault;
                const alienWidth = 38; // Slightly smaller
                const alienHeight = 28;
                const alienPadding = 12;
                let alienDirection = 1;
                let baseAlienSpeed = 0.4; // Base speed
                let alienSpeed = baseAlienSpeed;
                let level = 1;

                const alienColors = ['#FF4136', '#FFDC00', '#0074D9', '#B10DC9']; // More vibrant

                function initAliens() {{
                    aliens = [];
                    alienSpeed = baseAlienSpeed + (level - 1) * 0.15;
                    // alienRows = Math.min(alienRowsDefault + Math.floor((level-1)/2), 6); // Optionally increase rows
                    // alienCols = Math.min(alienColsDefault + Math.floor((level-1)/2), 10); // Optionally increase cols

                    for (let r = 0; r < alienRows; r++) {{
                        for (let c = 0; c < alienCols; c++) {{
                            const alien = {{
                                x: c * (alienWidth + alienPadding) + (canvas.width - (alienCols * (alienWidth + alienPadding) - alienPadding)) / 2, // Center aliens
                                y: r * (alienHeight + alienPadding) + 50,
                                width: alienWidth,
                                height: alienHeight,
                                alive: true,
                                color: alienColors[r % alienColors.length]
                            }};
                            aliens.push(alien);
                        }}
                    }}
                }}

                initAliens();

                document.addEventListener('keydown', function(e) {{
                    if (e.key === 'ArrowLeft' || e.key.toLowerCase() === 'a') player.isMovingLeft = true;
                    if (e.key === 'ArrowRight' || e.key.toLowerCase() === 'd') player.isMovingRight = true;

                    if (e.key === ' ' && !gameOver && player.shootCooldown <= 0) {{
                        e.preventDefault();
                        bullets.push({{
                            x: player.x + player.width / 2 - bulletWidth / 2,
                            y: player.y, width: bulletWidth, height: bulletHeight, color: '#FFFFFF'
                        }});
                        player.shootCooldown = player.shootCooldownMax;
                    }}
                    if (e.key === 'Enter' && gameOver) {{
                        resetGame();
                    }}
                }});

                document.addEventListener('keyup', function(e) {{
                    if (e.key === 'ArrowLeft' || e.key.toLowerCase() === 'a') player.isMovingLeft = false;
                    if (e.key === 'ArrowRight' || e.key.toLowerCase() === 'd') player.isMovingRight = false;
                }});

                function resetGame() {{
                    score = 0;
                    lives = 3;
                    level = 1;
                    gameOver = false;
                    gameOverSentToPython = false; // Reset this flag
                    player.x = canvas.width / 2 - player.width / 2;
                    player.isMovingLeft = false; player.isMovingRight = false;
                    bullets = [];
                    initAliens();
                    sendDataToStreamlit({{ score: score, lives: lives, gameOver: gameOver, level: level }});
                    requestAnimationFrame(gameLoop);
                }}

                function checkCollision(rect1, rect2) {{
                    return rect1.x < rect2.x + rect2.width &&
                           rect1.x + rect1.width > rect2.x &&
                           rect1.y < rect2.y + rect2.height &&
                           rect1.y + rect1.height > rect2.y;
                }}

                function drawPlayer() {{
                    ctx.fillStyle = player.color;
                    ctx.fillRect(player.x, player.y, player.width, player.height);
                    ctx.fillStyle = '#FFFFFF'; // Cockpit
                    ctx.fillRect(player.x + player.width/2 - 4, player.y + 7, 8, 8);
                }}

                function drawAlien(alien) {{
                    ctx.fillStyle = alien.color;
                    ctx.fillRect(alien.x, alien.y, alien.width, alien.height);
                    ctx.fillStyle = 'black'; // Eyes
                    ctx.fillRect(alien.x + alien.width * 0.25, alien.y + alien.height * 0.3, 4, 4);
                    ctx.fillRect(alien.x + alien.width * 0.65, alien.y + alien.height * 0.3, 4, 4);
                }}

                let frameCountForStreamlitUpdate = 0;

                function gameLoop() {{
                    if (gameOver) {{
                        ctx.fillStyle = 'rgba(0, 0, 0, 0.85)'; // Darker overlay
                        ctx.fillRect(0, 0, canvas.width, canvas.height);
                        ctx.fillStyle = '#FFFFFF';
                        ctx.font = '50px "Courier New", Courier, monospace'; // Retro font
                        ctx.textAlign = 'center';
                        ctx.fillText('GAME OVER', canvas.width / 2, canvas.height / 2 - 70);
                        ctx.font = '30px "Courier New", Courier, monospace';
                        ctx.fillText('Final Score: ' + score, canvas.width / 2, canvas.height / 2 - 20);
                        ctx.font = '22px "Courier New", Courier, monospace';
                        ctx.fillText('Press Enter to Restart', canvas.width / 2, canvas.height / 2 + 30);

                        if (!gameOverSentToPython) {{
                             sendDataToStreamlit({{ score: score, lives: lives, gameOver: true, level: level }});
                             gameOverSentToPython = true;
                        }}
                        return;
                    }}

                    ctx.clearRect(0, 0, canvas.width, canvas.height);

                    if (player.isMovingLeft && player.x > 0) player.x -= player.speed;
                    if (player.isMovingRight && player.x < canvas.width - player.width) player.x += player.speed;
                    drawPlayer();

                    if (player.shootCooldown > 0) player.shootCooldown--;

                    for (let i = bullets.length - 1; i >= 0; i--) {{
                        const bullet = bullets[i];
                        bullet.y -= bulletSpeed;
                        ctx.fillStyle = bullet.color;
                        ctx.fillRect(bullet.x, bullet.y, bullet.width, bullet.height);

                        if (bullet.y + bullet.height < 0) {{ bullets.splice(i, 1); continue; }}

                        for (let j = aliens.length - 1; j >= 0; j--) {{
                            const alien = aliens[j];
                            if (alien.alive && checkCollision(bullet, alien)) {{
                                alien.alive = false;
                                bullets.splice(i, 1);
                                score += 10 * level;
                                if (aliens.every(a => !a.alive)) {{
                                    level++;
                                    initAliens();
                                }}
                                break;
                            }}
                        }}
                    }}

                    let moveDown = false;
                    let advanceAliens = true; // Flag to control alien horizontal movement

                    for (const alien of aliens) {{
                        if (alien.alive) {{
                            if (alien.x + alien.width + (alienSpeed * alienDirection) > canvas.width || alien.x + (alienSpeed * alienDirection) < 0) {{
                                moveDown = true;
                                advanceAliens = false; // Don't advance horizontally on the same frame as moving down
                                break;
                            }}
                        }}
                    }}

                    if (moveDown) {{
                        alienDirection *= -1;
                        for (const alien of aliens) {{
                            if (alien.alive) {{
                                alien.y += alienHeight / 1.5; // Move down a bit more
                                 if (alien.y + alien.height >= player.y - 5) {{
                                    lives = 0; gameOver = true; break;
                                }}
                            }}
                        }}
                    }}

                    if(advanceAliens && !gameOver) {{ // Only move horizontally if not moving down and not game over
                         for (const alien of aliens) {{
                            if (alien.alive) {{
                                alien.x += alienSpeed * alienDirection;
                            }}
                        }}
                    }}

                    for (const alien of aliens) {{
                        if (alien.alive) {{
                            drawAlien(alien);
                            if (checkCollision(alien, player)) {{
                                lives--;
                                if (lives <= 0) {{ lives = 0; gameOver = true; }}
                                else {{
                                    player.x = canvas.width / 2 - player.width / 2;
                                    initAliens(); // Reset wave on player hit
                                }}
                                break;
                            }}
                        }}
                    }}

                    ctx.fillStyle = '#FFFFFF';
                    ctx.font = '18px "Courier New", Courier, monospace';
                    ctx.textAlign = 'left';
                    ctx.fillText('Score: ' + score, 15, 30);
                    ctx.textAlign = 'right';
                    ctx.fillText('Lives: ' + (lives > 0 ? '❤️'.repeat(lives) : '💔'), canvas.width - 15, 30);
                    ctx.textAlign = 'center';
                    ctx.fillText('Level: ' + level, canvas.width/2, 30);

                    frameCountForStreamlitUpdate++;
                    if (frameCountForStreamlitUpdate >= 20 && !gameOver) {{ // Update Streamlit every ~1/3 second
                        sendDataToStreamlit({{ score: score, lives: lives, gameOver: gameOver, level: level }});
                        frameCountForStreamlitUpdate = 0;
                    }}

                    requestAnimationFrame(gameLoop);
                }}

                canvas.setAttribute('tabindex', '0');
                canvas.focus();

                sendDataToStreamlit({{ score: score, lives: lives, gameOver: gameOver, level: level }}); // Initial data send
                requestAnimationFrame(gameLoop);
            </script>
        </body>
        </html>
        """

        # Removed 'key' argument here
        game_data_from_js = st.components.v1.html(game_html, height=620, scrolling=False)

        if game_data_from_js:  # This will be None until JS sends data
            try:
                data = json.loads(game_data_from_js)
                js_score = data.get("score", st.session_state.score)
                js_lives = data.get("lives", st.session_state.lives)
                js_game_over = data.get("gameOver", False)
                # js_level = data.get("level", 1) # Can also track level in Python if needed

                # Check if session state needs update
                should_rerun_for_game_over = False
                if st.session_state.score != js_score or st.session_state.lives != js_lives:
                    st.session_state.score = js_score
                    st.session_state.lives = js_lives
                    # Metrics will update on their own, no rerun needed for just score/lives change

                if js_game_over and st.session_state.game_active:  # Game ended in JS
                    st.toast(f"游戏结束! 最终得分: {st.session_state.score}", icon="🏁")
                    st.session_state.game_active = False
                    if st.session_state.user_id: # Save score only if user is logged in
                        database.save_game_score(st.session_state.user_id, "Space Invaders", st.session_state.score)
                        st.toast(f"分数 {st.session_state.score} 已保存!", icon="💾")
                    should_rerun_for_game_over = True

                if should_rerun_for_game_over:
                    st.rerun()  # Rerun only if game over state changes UI significantly

            except (json.JSONDecodeError, TypeError):
                # st.warning(f"Error processing game data from JS. Data: {game_data_from_js}")
                pass

        st.info("ℹ️ 点击游戏画布以获取键盘焦点。 (Click on the game canvas to focus keyboard input.)")

    else:  # Game not active
        st.markdown("<br>", unsafe_allow_html=True)
        try:
            # Ensure 'cover.png' is in the same directory as your script
            st.image("cover.png", use_container_width=True, caption="Space Invaders - 点击侧边栏开始游戏!")
        except Exception:  # Catch FileNotFoundError and other potential image loading issues
            st.subheader("👾 Space Invaders 👾")
            st.write("点击侧边栏的 '开始游戏' 来启动！(Click 'Start Game' in the sidebar to begin!)")
        st.markdown(
            """
            <div style="text-align: center; margin-top: 20px;">
                <h4>准备好保卫地球了吗？(Ready to defend Earth?)</h4>
            </div>
            """, unsafe_allow_html=True
        )