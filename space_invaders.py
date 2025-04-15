import streamlit as st
import time
import random
import json

# 设置页面配置
st.set_page_config(page_title="Space Invaders", layout="wide")

# 游戏状态管理
if 'game_active' not in st.session_state:
    st.session_state.game_active = False
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'high_score' not in st.session_state:
    st.session_state.high_score = 0
if 'lives' not in st.session_state:
    st.session_state.lives = 3

# 游戏标题
st.title("Space Invaders")

# 游戏说明
with st.expander("游戏说明"):
    st.markdown("""
    ### 游戏规则：
    - 使用键盘的左右箭头键移动你的飞船
    - 使用空格键发射子弹
    - 击中外星人获得分数
    - 避免被外星人击中或让外星人到达底部
    - 每关卡外星人移动速度会增加
    
    ### 控制：
    - ← : 向左移动
    - → : 向右移动
    - 空格键 : 发射子弹
    """)

# 游戏界面
col1, col2 = st.columns([3, 1])

with col2:
    st.subheader("游戏状态")
    st.metric("分数", st.session_state.score)
    st.metric("最高分", st.session_state.high_score)
    st.metric("生命值", st.session_state.lives)
    
    if not st.session_state.game_active:
        if st.button("开始游戏", key="start_game"):
            st.session_state.game_active = True
            st.session_state.score = 0
            st.session_state.lives = 3
            st.rerun()
    else:
        if st.button("结束游戏", key="end_game"):
            st.session_state.game_active = False
            if st.session_state.score > st.session_state.high_score:
                st.session_state.high_score = st.session_state.score
            st.rerun()

with col1:
    # 使用HTML Canvas实现游戏
    if st.session_state.game_active:
        # 创建游戏画布
        game_html = """
        <style>
            #gameCanvas {
                border: 2px solid white;
                background-color: black;
                display: block;
                margin: 0 auto;
            }
            body {
                overflow: hidden;
                margin: 0;
            }
        </style>
        <canvas id="gameCanvas" width="800" height="600"></canvas>
        <script>
            // 游戏初始化
            const canvas = document.getElementById('gameCanvas');
            const ctx = canvas.getContext('2d');
            
            // 游戏变量
            let score = 0;
            let lives = 3;
            let gameOver = false;
            
            // 玩家飞船
            const player = {
                x: canvas.width / 2 - 25,
                y: canvas.height - 60,
                width: 50,
                height: 30,
                speed: 8,
                color: '#00FF00',
                isMovingLeft: false,
                isMovingRight: false
            };
            
            // 子弹数组
            let bullets = [];
            const bulletSpeed = 7;
            
            // 外星人数组
            let aliens = [];
            const alienRows = 5;
            const alienCols = 10;
            const alienWidth = 40;
            const alienHeight = 30;
            const alienPadding = 10;
            let alienDirection = 1;
            let alienSpeed = 1;
            
            // 初始化外星人
            function initAliens() {
                aliens = [];
                for (let r = 0; r < alienRows; r++) {
                    for (let c = 0; c < alienCols; c++) {
                        const alien = {
                            x: c * (alienWidth + alienPadding) + 50,
                            y: r * (alienHeight + alienPadding) + 50,
                            width: alienWidth,
                            height: alienHeight,
                            alive: true,
                            color: r === 0 ? '#FF0000' : (r < 3 ? '#FFFF00' : '#00FFFF')
                        };
                        aliens.push(alien);
                    }
                }
            }
            
            // 初始化游戏
            initAliens();
            
            // 键盘控制
            document.addEventListener('keydown', function(e) {
                if (e.key === 'ArrowLeft') {
                    player.isMovingLeft = true;
                }
                if (e.key === 'ArrowRight') {
                    player.isMovingRight = true;
                }
                if (e.key === ' ' && !gameOver) {
                    // 发射子弹
                    bullets.push({
                        x: player.x + player.width / 2 - 2,
                        y: player.y,
                        width: 4,
                        height: 10,
                        color: '#FFFFFF'
                    });
                }
                if (e.key === 'Enter' && gameOver) {
                    // 重新开始游戏
                    resetGame();
                }
            });
            
            document.addEventListener('keyup', function(e) {
                if (e.key === 'ArrowLeft') {
                    player.isMovingLeft = false;
                }
                if (e.key === 'ArrowRight') {
                    player.isMovingRight = false;
                }
            });
            
            // 重置游戏
            function resetGame() {
                score = 0;
                lives = 3;
                gameOver = false;
                player.x = canvas.width / 2 - 25;
                bullets = [];
                initAliens();
                alienSpeed = 1;
            }
            
            // 检测碰撞
            function checkCollision(rect1, rect2) {
                return rect1.x < rect2.x + rect2.width &&
                       rect1.x + rect1.width > rect2.x &&
                       rect1.y < rect2.y + rect2.height &&
                       rect1.y + rect1.height > rect2.y;
            }
            
            // 游戏主循环
            function gameLoop() {
                // 清除画布
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                if (!gameOver) {
                    // 移动玩家
                    if (player.isMovingLeft && player.x > 0) {
                        player.x -= player.speed;
                    }
                    if (player.isMovingRight && player.x < canvas.width - player.width) {
                        player.x += player.speed;
                    }
                    
                    // 绘制玩家飞船
                    ctx.fillStyle = player.color;
                    ctx.beginPath();
                    // 飞船主体
                    ctx.moveTo(player.x + player.width / 2, player.y); // 飞船顶部
                    ctx.lineTo(player.x + player.width, player.y + player.height); // 右下角
                    ctx.lineTo(player.x, player.y + player.height); // 左下角
                    ctx.closePath();
                    ctx.fill();
                    
                    // 飞船驾驶舱
                    ctx.fillStyle = '#FFFFFF';
                    ctx.beginPath();
                    ctx.arc(player.x + player.width / 2, player.y + player.height / 2, player.width / 6, 0, Math.PI * 2);
                    ctx.fill();
                    
                    // 移动和绘制子弹
                    for (let i = 0; i < bullets.length; i++) {
                        bullets[i].y -= bulletSpeed;
                        
                        // 移除超出屏幕的子弹
                        if (bullets[i].y < 0) {
                            bullets.splice(i, 1);
                            i--;
                            continue;
                        }
                        
                        // 绘制子弹
                        ctx.fillStyle = bullets[i].color;
                        ctx.beginPath();
                        ctx.arc(bullets[i].x + bullets[i].width / 2, bullets[i].y + bullets[i].height / 2, bullets[i].width, 0, Math.PI * 2);
                        ctx.fill();
                        
                        // 检测子弹与外星人的碰撞
                        for (let j = 0; j < aliens.length; j++) {
                            if (aliens[j].alive && checkCollision(bullets[i], aliens[j])) {
                                // 击中外星人
                                aliens[j].alive = false;
                                bullets.splice(i, 1);
                                i--;
                                score += 10;
                                
                                // 检查是否所有外星人都被消灭
                                const allDead = aliens.every(alien => !alien.alive);
                                if (allDead) {
                                    // 下一关卡
                                    initAliens();
                                    alienSpeed += 0.5;
                                }
                                
                                break;
                            }
                        }
                    }
                    
                    // 移动和绘制外星人
                    let changeDirection = false;
                    let alienReachedBottom = false;
                    
                    for (let i = 0; i < aliens.length; i++) {
                        if (!aliens[i].alive) continue;
                        
                        // 检查是否需要改变方向
                        if ((aliens[i].x + aliens[i].width + alienSpeed * alienDirection > canvas.width) ||
                            (aliens[i].x + alienSpeed * alienDirection < 0)) {
                            changeDirection = true;
                        }
                        
                        // 检查是否到达底部
                        if (aliens[i].y + aliens[i].height > player.y) {
                            alienReachedBottom = true;
                        }
                        
                        // 绘制外星人
                        ctx.fillStyle = aliens[i].color;
                        ctx.beginPath();
                        
                        // 外星人头部
                        ctx.arc(aliens[i].x + aliens[i].width / 2, aliens[i].y + aliens[i].height / 3, aliens[i].width / 3, 0, Math.PI * 2);
                        ctx.fill();
                        
                        // 外星人身体
                        ctx.beginPath();
                        ctx.moveTo(aliens[i].x, aliens[i].y + aliens[i].height / 2); // 左上
                        ctx.lineTo(aliens[i].x + aliens[i].width, aliens[i].y + aliens[i].height / 2); // 右上
                        ctx.lineTo(aliens[i].x + aliens[i].width, aliens[i].y + aliens[i].height); // 右下
                        ctx.lineTo(aliens[i].x, aliens[i].y + aliens[i].height); // 左下
                        ctx.closePath();
                        ctx.fill();
                        
                        // 外星人眼睛
                        ctx.fillStyle = '#000000';
                        ctx.beginPath();
                        ctx.arc(aliens[i].x + aliens[i].width / 3, aliens[i].y + aliens[i].height / 3, aliens[i].width / 10, 0, Math.PI * 2);
                        ctx.arc(aliens[i].x + aliens[i].width * 2/3, aliens[i].y + aliens[i].height / 3, aliens[i].width / 10, 0, Math.PI * 2);
                        ctx.fill();
                        
                        // 外星人触角
                        ctx.strokeStyle = aliens[i].color;
                        ctx.lineWidth = 2;
                        ctx.beginPath();
                        ctx.moveTo(aliens[i].x + aliens[i].width / 3, aliens[i].y);
                        ctx.lineTo(aliens[i].x + aliens[i].width / 3, aliens[i].y - aliens[i].height / 4);
                        ctx.moveTo(aliens[i].x + aliens[i].width * 2/3, aliens[i].y);
                        ctx.lineTo(aliens[i].x + aliens[i].width * 2/3, aliens[i].y - aliens[i].height / 4);
                        ctx.stroke();
                        
                        // 检测外星人与玩家的碰撞
                        if (checkCollision(aliens[i], player)) {
                            lives--;
                            if (lives <= 0) {
                                gameOver = true;
                            } else {
                                // 重置玩家位置
                                player.x = canvas.width / 2 - 25;
                            }
                        }
                    }
                    
                    // 改变外星人方向并下移
                    if (changeDirection) {
                        alienDirection *= -1;
                        for (let i = 0; i < aliens.length; i++) {
                            if (aliens[i].alive) {
                                aliens[i].y += 20;
                            }
                        }
                    } else {
                        // 正常移动外星人
                        for (let i = 0; i < aliens.length; i++) {
                            if (aliens[i].alive) {
                                aliens[i].x += alienSpeed * alienDirection;
                            }
                        }
                    }
                    
                    // 检查外星人是否到达底部
                    if (alienReachedBottom) {
                        lives--;
                        if (lives <= 0) {
                            gameOver = true;
                        } else {
                            // 重置外星人和玩家位置
                            initAliens();
                            player.x = canvas.width / 2 - 25;
                        }
                    }
                    
                    // 显示分数和生命值
                    ctx.fillStyle = '#FFFFFF';
                    ctx.font = '20px Arial';
                    ctx.fillText('分数: ' + score, 10, 30);
                    ctx.fillText('生命: ' + lives, canvas.width - 100, 30);
                    
                    // 更新Streamlit中的分数
                    if (window.parent && window.parent.streamlit) {
                        const scores = {
                            score: score,
                            lives: lives
                        };
                        window.parent.streamlit.setComponentValue(JSON.stringify(scores));
                    }
                } else {
                    // 游戏结束画面
                    ctx.fillStyle = '#FFFFFF';
                    ctx.font = '40px Arial';
                    ctx.textAlign = 'center';
                    ctx.fillText('游戏结束', canvas.width / 2, canvas.height / 2 - 40);
                    ctx.font = '25px Arial';
                    ctx.fillText('最终分数: ' + score, canvas.width / 2, canvas.height / 2);
                    ctx.fillText('按Enter键重新开始', canvas.width / 2, canvas.height / 2 + 40);
                }
                
                // 继续游戏循环
                requestAnimationFrame(gameLoop);
            }
            
            // 开始游戏循环
            gameLoop();
        </script>
        """
        
        # 使用components.html显示游戏
        st.components.v1.html(game_html, height=650)
        
        # 添加键盘焦点提示
        st.info("点击游戏画布以获取键盘焦点，然后使用方向键和空格键进行游戏。")
    else:
        # 显示游戏封面图片
        st.image("cover.png", use_container_width=True)