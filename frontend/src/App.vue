<template>
  <div class="app" :class="{ 'egg-active': showEggPage }">
    <!-- Floating petals -->
    <div class="petals">
      <span v-for="i in 12" :key="i" class="petal" :style="petalStyle(i)">·</span>
    </div>

    <!-- Header -->
    <header class="header">
      <div class="header-inner">
        <h1 class="logo" @click="logoClicks++; checkLogoEgg(); activeSection = 'home'">
          <img src="/logo.svg" alt="diary" class="logo-img" />
        </h1>
        <div class="header-actions">
          <!-- Login button -->
          <button v-if="!currentUser" class="login-trigger" @click="showLoginModal = true">
            <span class="login-icon">👤</span>
          </button>
          <!-- User menu -->
          <div v-else class="user-menu" @click="showUserMenu = !showUserMenu">
            <span class="login-icon logged" :style="getAvatarStyle(currentUser)" :class="{ 'no-avatar-text': currentUser.avatar }">{{ currentUser.avatar ? '' : (currentUser.nickname?.charAt(0) || currentUser.username?.charAt(0)) }}</span>
            <transition name="fade">
              <div v-if="showUserMenu" class="user-dropdown" @click.stop>
                <div class="ud-name">{{ currentUser.nickname || currentUser.username }}</div>
                <button class="ud-item" @click="showUserMenu = false">{{ t('myPrivate') }}</button>
                <button class="ud-item ud-logout" @click="logout">{{ t('logout') }}</button>
              </div>
            </transition>
          </div>
          <div class="lang-switcher">
            <button v-for="lang in languages" :key="lang.code"
              :class="['lang-btn', { active: currentLang === lang.code }]"
              @click="currentLang = lang.code">{{ lang.label }}</button>
          </div>
        </div>
      </div>
    </header>

    <!-- Login Modal -->
    <transition name="fade">
      <div v-if="showLoginModal" class="modal-overlay" @click.self="showLoginModal = false">
        <div class="login-modal">
          <div class="login-tabs">
            <button :class="['login-tab', { active: loginMode === 'login' }]" @click="loginMode = 'login'">{{ t('login') }}</button>
            <button :class="['login-tab', { active: loginMode === 'register' }]" @click="loginMode = 'register'">{{ t('register') }}</button>
          </div>
          <input v-model="authUsername" type="text" :placeholder="t('username')" class="modal-input" />
          <input v-model="authPassword" type="password" :placeholder="t('password')" class="modal-input" />
          <input v-if="loginMode === 'register'" v-model="authNickname" type="text" :placeholder="t('nickname')" class="modal-input" />
          <div v-if="authError" class="auth-error">{{ authError }}</div>
          <button class="submit-btn" @click="handleAuth" :disabled="authLoading">
            {{ authLoading ? '...' : (loginMode === 'login' ? t('login') : t('register')) }}
          </button>
        </div>
      </div>
    </transition>

    <!-- Bottom Nav -->
    <nav class="bottom-nav">
      <button v-for="item in navItems" :key="item.id"
        :class="['bnav-btn', { active: activeSection === item.id }]"
        @click="navigateTo(item.id)">
        <span class="bnav-icon">{{ item.icon }}</span>
        <span class="bnav-label">{{ t(item.id) }}</span>
      </button>
    </nav>

    <!-- Main -->
    <main class="main" @click.capture="onGlobalClick">

      <!-- ===== HOME / PROFILE ===== -->
      <section v-if="activeSection === 'home'" class="section">
        <!-- Profile Header -->
        <div class="profile-header">
          <div class="profile-avatar-wrap">
            <div class="profile-avatar" :style="currentUser?.avatar ? `background-image: url('http://localhost:520/uploads/${currentUser.avatar}'); background-size: cover; background-position: center;` : ''" :class="{ 'no-avatar': !currentUser?.avatar }" @dblclick="miniEgg">
              <span v-if="!currentUser?.avatar" style="color:#8e8e8e;font-size:24px;font-weight:300">diary</span>
            </div>
            <div class="avatar-ring"></div>
          </div>
          <div class="profile-info">
            <h2 class="profile-name">{{ currentUser ? (currentUser.nickname || currentUser.username) : 'diary' }}</h2>
            <p class="profile-bio">{{ t('profileBio') }}</p>
          </div>
        </div>

        <!-- Stats -->
        <div class="profile-stats">
          <div class="pstat" @click="navigateTo('gallery')">
            <span class="pstat-num">{{ stats.photos }}</span>
            <span class="pstat-label">{{ t('photos') }}</span>
          </div>
          <div class="pstat-divider"></div>
          <div class="pstat" @click="navigateTo('messages')">
            <span class="pstat-num">{{ stats.messages }}</span>
            <span class="pstat-label">{{ t('messages') }}</span>
          </div>
          <div class="pstat-divider"></div>
          <div class="pstat">
            <span class="pstat-num">{{ stats.total_likes }}</span>
            <span class="pstat-label">{{ t('likes') }}</span>
          </div>
        </div>

        <!-- Stories -->
        <div class="stories-bar">
          <div class="story-item" v-for="s in stories" :key="s.id"
            :class="{ viewed: s.viewed }" @click="viewStory(s)">
            <div class="story-ring">
              <div class="story-thumb">{{ s.icon }}</div>
            </div>
            <span class="story-name">{{ s.name }}</span>
          </div>
        </div>

        <!-- Featured Quote -->
        <div class="feature-card" @click="quoteEgg">
          <div class="feature-icon">✨</div>
          <p class="feature-text">{{ t('heroLine1') }}</p>
          <p class="feature-text accent">{{ t('heroLine2') }}</p>
          <div class="feature-dots">
            <span v-for="i in 3" :key="i" :class="['dot', { active: currentQuote === i-1 }]"></span>
          </div>
        </div>
      </section>

      <!-- ===== GALLERY / FEED ===== -->
      <section v-if="activeSection === 'gallery'" class="section">
        <div class="section-head">
          <h2 class="section-title">{{ t('ourMoments') }}</h2>
          <div class="section-head-actions">
            <input v-model="gallerySearch" type="text" :placeholder="t('searchPlaceholder')" class="inline-search" @keyup.enter="doGallerySearch" />
            <label class="upload-btn">
              <input type="file" accept="image/*" @change="onFileSelect" hidden />
              <span class="upload-icon">+</span>
            </label>
          </div>
        </div>

        <!-- Upload Modal -->
        <div v-if="showUploadModal" class="modal-overlay" @click.self="showUploadModal = false">
          <div class="modal">
            <div class="modal-preview" v-if="uploadPreview">
              <img :src="uploadPreview" alt="preview" />
            </div>
            <input v-model="uploadCaption" type="text" :placeholder="t('writeCaption')" class="modal-input" />
            <div v-if="uploadLocation" class="upload-location">
              <span>📍</span> {{ uploadLocation }}
            </div>
            <label v-if="currentUser" class="private-toggle" style="margin-bottom:14px">
              <input type="checkbox" v-model="uploadIsPrivate" />
              <span class="private-label">{{ uploadIsPrivate ? '🔒' : '🔓' }} {{ t('private') }}</span>
            </label>
            <div class="modal-actions">
              <button class="btn-cancel" @click="showUploadModal = false">{{ t('cancel') }}</button>
              <button class="btn-confirm" @click="confirmUpload" :disabled="uploading">
                {{ uploading ? '...' : '✨' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Instagram Feed -->
        <div class="feed" v-if="filteredPhotos.length">
          <div v-for="photo in filteredPhotos" :key="photo.id" class="post-card" :class="{ 'post-private': photo.is_private }">
            <!-- Post Header -->
            <div class="post-header">
              <div class="post-avatar" :style="photo.author_avatar ? `background-image: url('${UPLOAD_BASE}${photo.author_avatar}'); background-size: cover; background-position: center;` : ''" :class="{ 'no-avatar-text': photo.author_avatar }">
                <span v-if="!photo.author_avatar" style="font-size:12px;color:#8e8e8e">●</span>
              </div>
              <div class="post-user-info">
                <span class="post-username">{{ photo.author_name || 'diary' }}</span>
                <span class="post-location">{{ photo.location || t('inMyHeart') }}</span>
                <span v-if="isPhotoOwner(photo)" class="msg-private-badge">{{ photo.is_private ? '🔒' : '🔓' }}</span>
                <span v-else-if="photo.is_private" class="msg-private-badge">🔒</span>
              </div>
              <!-- Owner actions -->
              <div v-if="isPhotoOwner(photo)" class="post-owner-actions">
                <button class="post-action-sm" @click="startEditPhoto(photo)" title="edit">✏️</button>
                <button class="post-action-sm" @click="togglePhotoPrivate(photo)" :title="photo.is_private ? t('setPublic') : t('setPrivate')">
                  {{ photo.is_private ? '🔒' : '🔓' }}
                </button>
                <button class="post-action-sm" @click="handleDeletePhoto(photo.id)" title="delete">🗑️</button>
              </div>
            </div>

            <!-- Edit photo caption -->
            <div v-if="editingPhotoId === photo.id" class="photo-edit-wrap">
              <input v-model="editingPhotoCaption" type="text" class="modal-input" :placeholder="t('writeCaption')" style="margin:0 14px 8px" />
              <div class="photo-edit-actions" style="padding:0 14px 12px;display:flex;gap:8px;justify-content:flex-end">
                <button class="btn-cancel" @click="editingPhotoId = null" style="font-size:12px;padding:6px 14px">{{ t('cancel') }}</button>
                <button class="btn-confirm" @click="confirmEditPhoto(photo.id)" style="font-size:12px;padding:6px 14px">{{ t('save') }}</button>
              </div>
            </div>

            <!-- Post Image (double tap to like) -->
            <div class="post-image-wrap" @dblclick="doubleTapLike(photo, $event)">
              <img :src="getPhotoUrl(photo.filename)" :alt="photo.caption" loading="lazy" />
              <!-- Double-tap star animation -->
              <transition name="heart-pop">
                <div v-if="tapHeart === photo.id" class="double-tap-heart">✨</div>
              </transition>
            </div>

            <!-- Post Actions -->
            <div class="post-actions">
              <div class="post-actions-left">
                <button :class="['action-btn', { liked: photoLikedSet.has(photo.id) }]"
                  @click="togglePhotoLike(photo)">
                  {{ photoLikedSet.has(photo.id) ? '⭐' : '☆' }}
                </button>
                <button class="action-btn" @click="openComments(photo)">💬</button>
              </div>
              <button class="action-btn" @click="bookmarkEgg">🔖</button>
            </div>

            <!-- Likes -->
            <div class="post-likes" v-if="photo.likes > 0">
              {{ photo.likes }} {{ t('peopleLike') }}
            </div>

            <!-- Caption -->
            <div class="post-caption" v-if="photo.caption && editingPhotoId !== photo.id">
              <strong>{{ photo.author_name || 'diary' }}</strong> {{ photo.caption }}
            </div>

            <!-- View comments -->
            <div class="post-view-comments" v-if="photo.comments_count > 2" @click="openComments(photo)">
              {{ t('viewAllComments', [photo.comments_count]) }}
            </div>

            <!-- Recent Comments -->
            <div class="post-recent-comments" v-if="photo.recent_comments && photo.recent_comments.length">
              <div v-for="c in photo.recent_comments.slice(0,2)" :key="c.id" class="post-comment-item">
                <strong>{{ c.nickname }}</strong> {{ c.content }}
              </div>
            </div>

            <!-- Quick Comment -->
            <div class="post-comment-input">
              <input :placeholder="t('addComment')" class="quick-comment"
                @keyup.enter="quickComment(photo, $event)" />
              <button class="comment-send" @click="quickComment(photo, $event)">{{ t('post') }}</button>
            </div>

            <!-- Time -->
            <div class="post-time">{{ formatTimeAgo(photo.created_at) }}</div>
          </div>
        </div>

        <div v-else class="empty-state">
          <span class="empty-icon">🎞️</span>
          <p>{{ t('noPhotos') }}</p>
        </div>
      </section>

      <!-- ===== COMMENTS FULL ===== -->
      <transition name="slide-up">
        <div v-if="showCommentsPanel" class="comments-panel">
          <div class="cp-header">
            <button class="cp-back" @click="showCommentsPanel = false">←</button>
            <span class="cp-title">{{ t('comments') }}</span>
            <div style="width:24px"></div>
          </div>
          <div class="cp-list">
            <div v-for="c in commentsList" :key="c.id" class="cp-item">
              <div class="cp-avatar" :style="c.avatar ? `background-image: url('${UPLOAD_BASE}${c.avatar}'); background-size: cover; background-position: center;` : ''" :class="{ 'no-avatar-text': c.avatar }">
                <span v-if="!c.avatar">{{ c.nickname.charAt(0) }}</span>
              </div>
              <div class="cp-body">
                <div class="cp-meta">
                  <strong>{{ c.nickname }}</strong>
                  <span class="cp-time">{{ formatTimeAgo(c.created_at) }}</span>
                  <div v-if="isCommentOwner(c)" class="cp-actions">
                    <button class="cp-action-btn" @click="startEditComment(c)" title="edit">✏️</button>
                    <button class="cp-action-btn cp-delete" @click="handleDeleteComment(c.id)" title="delete">🗑️</button>
                  </div>
                </div>
                <div v-if="editingCommentId === c.id" class="cp-edit-wrap">
                  <input v-model="editingCommentContent" class="cp-edit-input" @keyup.enter="confirmEditComment(c.id)" />
                  <div class="cp-edit-actions">
                    <button class="btn-cancel" @click="editingCommentId = null" style="font-size:12px;padding:6px 12px">{{ t('cancel') }}</button>
                    <button class="btn-confirm" @click="confirmEditComment(c.id)" style="font-size:12px;padding:6px 12px">{{ t('save') }}</button>
                  </div>
                </div>
                <p v-else>{{ c.content }}</p>
              </div>
            </div>
            <div v-if="!commentsList.length" class="cp-empty">{{ t('noComments') }}</div>
          </div>
          <div class="cp-input-bar">
            <input v-model="commentNickname" :placeholder="t('yourName')" class="cp-name" />
            <input v-model="commentText" :placeholder="t('addComment')" class="cp-input"
              @keyup.enter="submitComment" />
            <button class="cp-send" @click="submitComment">{{ t('post') }}</button>
          </div>
        </div>
      </transition>

      <!-- ===== PROFILE / MY CONTENT ===== -->
      <section v-if="activeSection === 'profile'" class="section">
        <!-- Profile Header -->
        <div class="profile-header">
          <div class="profile-avatar-wrap">
            <div class="profile-avatar lg-avatar" :style="getAvatarStyle(currentUser)" @click="avatarInput?.click()">
              <span v-if="!currentUser?.avatar" style="color:#8e8e8e;font-size:22px;font-weight:300">diary</span>
              <div class="avatar-edit-hint">✎</div>
            </div>
            <input ref="avatarInput" type="file" accept="image/*" style="display:none" @change="handleAvatarUpload">
            <div class="avatar-ring"></div>
          </div>
          <div class="profile-info">
            <h2 class="profile-name">{{ currentUser?.nickname || currentUser?.username || 'diary' }}</h2>
            <p class="profile-bio">{{ t('profileBio') }}</p>
          </div>
        </div>

        <!-- Login Required -->
        <div v-if="!currentUser" class="profile-login-required">
          <p>{{ t('loginFirst') }}</p>
          <button class="btn-primary" @click="showLoginModal = true">{{ t('login') }}</button>
        </div>

        <!-- My Content -->
        <div v-else>
          <!-- Tabs -->
          <div class="profile-tabs">
            <button :class="['ptab', { active: profileTab === 'photos' }]" @click="profileTab = 'photos'">{{ t('gallery') }}</button>
            <button :class="['ptab', { active: profileTab === 'messages' }]" @click="profileTab = 'messages'">{{ t('messages') }}</button>
          </div>

          <!-- My Photos -->
          <template v-if="profileTab === 'photos'">
            <div class="profile-grid" v-if="myPhotos.length">
              <div v-for="photo in myPhotos" :key="photo.id" class="pg-item">
                <img :src="getPhotoUrl(photo.filename)" @click="openPhotoDetail(photo)" />
              </div>
            </div>
            <div v-else class="profile-empty">{{ t('noPhotos') }}</div>
          </template>

          <!-- My Messages -->
          <template v-if="profileTab === 'messages'">
            <div class="msg-list" v-if="myMessages.length">
              <div v-for="msg in myMessages" :key="msg.id" class="msg-card">
                <div class="msg-avatar" :style="getAvatarStyle(currentUser)">
                  <span v-if="!currentUser?.avatar">{{ msg.nickname?.charAt(0) || '?' }}</span>
                </div>
                <div class="msg-body">
                  <div class="msg-meta">
                    <span class="msg-name">{{ msg.nickname }}</span>
                    <span v-if="msg.is_private" class="msg-private-badge">🔒</span>
                    <span class="msg-time">{{ msg.created_at }}</span>
                  </div>
                  <p>{{ msg.content }}</p>
                </div>
              </div>
            </div>
            <div v-else class="profile-empty">{{ t('noMessages') }}</div>
          </template>
        </div>
      </section>

      <!-- Profile Photo Modal -->
      <transition name="fade">
        <div v-if="profilePhotoModal" class="modal-overlay" @click.self="profilePhotoModal = null">
          <div class="ppm-wrap" @click.stop>
            <button class="ppm-close" @click="profilePhotoModal = null">×</button>
            <img :src="getPhotoUrl(profilePhotoModal.filename)" class="ppm-img" />
            <div class="ppm-info">
              <div class="ppm-header">
                <div class="post-avatar sm-avatar" :style="profilePhotoModal.author_avatar ? `background-image: url('${getPhotoUrl(profilePhotoModal.author_avatar)}'); background-size: cover; background-position: center;` : ''">
                  <span v-if="!profilePhotoModal.author_avatar" style="font-size:12px;color:#8e8e8e">●</span>
                </div>
                <div>
                  <div class="ppm-author">{{ profilePhotoModal.author_name || 'diary' }}</div>
                  <div class="ppm-location">{{ profilePhotoModal.location || t('inMyHeart') }}</div>
                </div>
              </div>
              <p class="ppm-caption">{{ profilePhotoModal.caption }}</p>
              <div class="ppm-stats">
                <span>⭐ {{ profilePhotoModal.likes || 0 }}</span>
                <span>💬 {{ profilePhotoModal.comments_count || 0 }}</span>
                <span>{{ profilePhotoModal.created_at }}</span>
              </div>
              <div class="ppm-actions" v-if="isPhotoOwner(profilePhotoModal)">
                <button class="ppm-btn" @click="togglePhotoPrivate(profilePhotoModal)">
                  {{ profilePhotoModal.is_private ? '🔓' : '🔒' }}
                </button>
                <button class="ppm-btn ppm-delete" @click="handleDeletePhoto(profilePhotoModal.id); profilePhotoModal = null">
                  🗑️
                </button>
              </div>
            </div>
          </div>
        </div>
      </transition>

      <!-- ===== MESSAGES / GUESTBOOK ===== -->
      <section v-if="activeSection === 'messages'" class="section">
        <div class="section-head">
          <h2 class="section-title">{{ t('guestbook') }}</h2>
          <div class="section-head-actions">
            <input v-model="msgSearch" type="text" :placeholder="t('searchPlaceholder')" class="inline-search" />
            <span class="msg-badge">{{ filteredMessages.length }}</span>
          </div>
        </div>

        <div class="msg-form">
          <div class="form-row">
            <input v-if="!currentUser" v-model="msgNickname" type="text" :placeholder="t('yourName')" class="form-input" />
            <div v-else class="form-input" style="background:var(--accent-light);border-color:var(--accent-soft);display:flex;align-items:center;padding-left:12px;gap:6px">
              <span style="font-size:14px">👤</span>
              <span style="font-size:13px;color:var(--text)">{{ currentUser.nickname || currentUser.username }}</span>
            </div>
            <div class="mood-selector">
              <button v-for="m in moods" :key="m.value"
                :class="['mood-btn', { active: msgMood === m.value }]"
                @click="msgMood = m.value" :title="t(m.key)">{{ m.icon }}</button>
            </div>
          </div>
          <textarea v-model="msgContent" :placeholder="t('writeMsg')" class="form-textarea" rows="3"></textarea>
          <div class="form-row-bottom">
            <label class="private-toggle" v-if="currentUser">
              <input type="checkbox" v-model="msgIsPrivate" />
              <span class="private-label">{{ msgIsPrivate ? '🔒' : '🔓' }} {{ t('private') }}</span>
            </label>
            <div v-else></div>
            <button class="submit-btn" @click="submitMessage" :disabled="!msgContent.trim()">{{ t('send') }}</button>
          </div>
        </div>

        <div class="msg-list" v-if="filteredMessages.length">
          <div v-for="msg in filteredMessages" :key="msg.id" class="msg-card" :class="{ 'msg-private': msg.is_private }">
            <div class="msg-avatar" :style="msg.author_avatar ? `background-image: url('${UPLOAD_BASE}${msg.author_avatar}'); background-size: cover; background-position: center;` : ''" :class="{ 'no-avatar-text': msg.author_avatar }">
              <span v-if="!msg.author_avatar">{{ msg.nickname.charAt(0) }}</span>
            </div>
            <div class="msg-body">
              <div class="msg-meta">
                <span class="msg-name">{{ msg.nickname }}</span>
                <span v-if="isMsgOwner(msg)" class="msg-private-badge">{{ msg.is_private ? '🔒' : '🔓' }}</span>
                <span v-else-if="msg.is_private" class="msg-private-badge">🔒</span>
                <span class="msg-time">{{ formatTimeAgo(msg.created_at) }}</span>
                <div v-if="isMsgOwner(msg)" class="msg-actions-menu">
                  <button class="msg-action-btn" @click="startEditMsg(msg)" title="edit">✏️</button>
                  <button class="msg-action-btn" @click="toggleMsgPrivate(msg)" :title="msg.is_private ? t('setPublic') : t('setPrivate')">
                    {{ msg.is_private ? '🔒' : '🔓' }}
                  </button>
                  <button class="msg-action-btn" @click="handleDeleteMsg(msg.id)" title="delete">🗑️</button>
                </div>
              </div>
              <!-- Edit mode -->
              <div v-if="editingMsgId === msg.id" class="msg-edit-wrap">
                <textarea v-model="editingMsgContent" class="form-textarea" rows="2" style="margin-bottom:8px"></textarea>
                <div class="msg-edit-actions">
                  <button class="btn-cancel" @click="editingMsgId = null" style="font-size:12px;padding:6px 14px">{{ t('cancel') }}</button>
                  <button class="btn-confirm" @click="confirmEditMsg(msg.id)" style="font-size:12px;padding:6px 14px">{{ t('save') }}</button>
                </div>
              </div>
              <p v-else class="msg-text">{{ msg.content }}</p>
              <button class="msg-like-btn" @click="toggleMsgLike(msg)">
                {{ msgLikedSet.has(msg.id) ? '⭐' : '☆' }} {{ msg.likes || 0 }}
              </button>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <span class="empty-icon">📝</span>
          <p>{{ t('noMessages') }}</p>
        </div>
      </section>

      <!-- ===== EASTER EGG PAGE ===== -->
      <transition name="egg-fade">
        <section v-if="showEggPage" class="section egg-page">
          <div class="egg-content" @click="eggClick++">
            <div class="egg-heart">✦</div>
            <h2 class="egg-title">{{ t('eggTitle') }}</h2>
            <p class="egg-text" v-html="t('eggText')"></p>
            <div class="egg-counter" v-if="eggClick > 5">
              <span>{{ eggClick }} {{ t('eggClicks') }}</span>
            </div>
            <div v-if="eggClick >= 20" class="egg-secret">
              🎉 {{ t('eggSecret') }}
            </div>
            <button class="egg-close" @click.stop="showEggPage = false">{{ t('back') }}</button>
          </div>
          <div class="egg-float-hearts">
            <span v-for="i in 30" :key="i" class="egg-fh" :style="eggFloatStyle(i)">✦</span>
          </div>
        </section>
      </transition>
    </main>

    <!-- Story Viewer -->
    <transition name="fade">
      <div v-if="showStoryViewer" class="story-viewer" @click="showStoryViewer = false">
        <div class="sv-bar" @click.stop>
          <div class="sv-progress"></div>
        </div>
        <div class="sv-content" @click.stop>
          <div class="sv-emoji">{{ viewingStory.icon }}</div>
          <p class="sv-text">{{ viewingStory.content }}</p>
        </div>
        <div class="sv-user" @click.stop>
          <span class="sv-name">{{ viewingStory.name }}</span>
        </div>
      </div>
    </transition>

    <!-- Footer -->
    <footer class="footer">
      <p>Made with care · {{ t('footer') }}</p>
    </footer>

    <!-- Login Required Popup -->
    <transition name="fade">
      <div v-if="showLoginRequiredPopup" class="modal-overlay" @click.self="onLoginRequiredCancel">
        <div class="confirm-box">
          <div class="confirm-icon">🔒</div>
          <p class="confirm-text">{{ t('loginRequiredPopup') }}</p>
          <div class="confirm-actions">
            <button class="btn-cancel" @click="onLoginRequiredCancel">{{ t('cancel') }}</button>
            <button class="btn-confirm" @click="onLoginRequiredConfirm">{{ t('ok') }}</button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Confirm Dialog -->
    <transition name="fade">
      <div v-if="confirmDialog.show" class="modal-overlay" @click.self="confirmDialog.onCancel">
        <div class="confirm-box">
          <div class="confirm-icon">{{ confirmDialog.icon || '⚠️' }}</div>
          <p class="confirm-text">{{ confirmDialog.message }}</p>
          <div class="confirm-actions">
            <button class="btn-cancel" @click="confirmDialog.onCancel">{{ t('cancel') }}</button>
            <button class="btn-confirm btn-danger" @click="confirmDialog.onConfirm">{{ t('deleteMsg') }}</button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Toast -->
    <transition name="toast">
      <div v-if="toast.show" class="toast" :class="toast.type">{{ toast.message }}</div>
    </transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import * as api from './api.js'

// ============ i18n ============
const currentLang = ref('ko')
const languages = [
  { code: 'ko', label: '한국어' },
  { code: 'zh', label: '中文' },
  { code: 'en', label: 'EN' },
  { code: 'ja', label: '日本語' },
]

const i18n = {
  ko: {
    appTitle: 'diary.', home: '홈', gallery: '갤러리', messages: '방명록',
    profileBio: '소소한 일상 기록 ✦',
    photos: '게시물', msgCount: '개 글', likes: '좋아요',
    heroLine1: '기억하고 싶은 순간들을', heroLine2: '여기에 모아두려고 해',
    ourMoments: '기록', uploadPhoto: '올리기',
    writeCaption: '문구를 적어보세요...',
    cancel: '취소', uploading: '...', post: '게시',
    noPhotos: '아직 사진이 없어요\n첫 사진을 올려보세요!',
    noComments: '아직 댓글이 없어요',
    guestbook: '방명록', comments: '댓글',
    yourName: '이름', writeMsg: '하고 싶은 말을 적어보세요...',
    send: '보내기', addComment: '댓글 달기...',
    noMessages: '아직 글이 없어요\n첫 글을 남겨보세요!',
    footer: 'everyday',
    mood_love: '평온', mood_happy: '행복', mood_miss: '그리움', mood_shy: '수줍음', mood_star: '별',
    toastPhotoOk: '업로드 완료 📸', toastPhotoFail: '실패, 다시 시도',
    toastMsgOk: '등록 완료 ✉️', toastMsgFail: '실패, 다시 시도',
    toastCommentOk: '댓글 완료 💬',
    anonymous: '익명',
    peopleLike: '명이 좋아합니다',
    viewAllComments: (n) => `댓글 ${n}개 모두 보기`,
    inMyHeart: '어딘가',
    ago: ' 전',
    eggTitle: '✦',
    eggText: '여기까지 와줘서 고마워<br>평범한 하루도<br>기록하면 특별해지니까<br><br>앞으로도 좋은 날들이<br>많았으면 좋겠어 ✨',
    eggClicks: '번 클릭!',
    eggSecret: '🤫 비밀 업적 달성',
    back: '닫기',
    login: '로그인', register: '회원가입', username: '아이디', password: '비밀번호', nickname: '별명',
    logout: '로그아웃', private: '나만 보기', setPrivate: '나만 보기', setPublic: '전체 공개',
    myPrivate: '나의 비밀글', save: '저장', editMsg: '수정', deleteMsg: '꺼내기',
    deleteConfirm: '이 기록을 걷어낼까요?',
    loginOk: '환영해요 ✨', registerOk: '가입 완료 ✨', authFail: '다시 시도해주세요',
    loginRequiredPopup: '로그인이 필요한 페이지입니다. 로그인 하시겠습니까?',
    ok: '확인',
    profile: '프로필', changeAvatar: '사진 변경', changeNickname: '별명 변경', phone: '전화번호', email: '이메일', changePwd: '비밀번호 변경', oldPwd: '현재 비밀번호', newPwd: '새 비밀번호', pwdChanged: '비밀번호 변경 완료 ✨', profileSaved: '저장 완료 ✨', loginFirst: '로그인 후 이용해주세요',
    timeJustNow: '방금', timeMin: '분', timeHour: '시간', timeDay: '일',
    story1: '어느 날 ☀️', story2: '기록 🌙', story3: '앞으로 🌸',
    story1Content: '기분 좋은 하루였어\n바람이 좋았어 🌿',
    story2Content: '소소한 순간들이\n자꾸 기억에 남아 📖',
    story3Content: '앞으로의 이야기도\n기록하고 싶어 ✨',
  },
  en: {
    appTitle: 'diary.', home: 'Home', gallery: 'Feed', messages: 'Board',
    profileBio: 'little moments ✦',
    photos: 'Posts', msgCount: 'msgs', likes: 'Likes',
    heroLine1: 'Moments I want to remember', heroLine2: 'collected here',
    ourMoments: 'Archive', uploadPhoto: 'Post',
    writeCaption: 'Write a caption...',
    cancel: 'Cancel', uploading: '...', post: 'Post',
    noPhotos: 'No photos yet\nUpload the first one!',
    noComments: 'No comments yet',
    guestbook: 'Guestbook', comments: 'Comments',
    yourName: 'Name', writeMsg: 'Write something...',
    send: 'Send', addComment: 'Add a comment...',
    noMessages: 'No messages yet\nLeave the first one!',
    footer: 'everyday',
    mood_love: 'Calm', mood_happy: 'Happy', mood_miss: 'Miss', mood_shy: 'Shy', mood_star: 'Star',
    toastPhotoOk: 'Uploaded 📸', toastPhotoFail: 'Failed, retry',
    toastMsgOk: 'Posted ✉️', toastMsgFail: 'Failed, retry',
    toastCommentOk: 'Commented 💬',
    anonymous: 'Anonymous',
    peopleLike: 'likes',
    viewAllComments: (n) => `View all ${n} comments`,
    inMyHeart: 'somewhere',
    ago: ' ago',
    eggTitle: '✦',
    eggText: 'Thanks for finding this page<br>Even ordinary days<br>become special when documented<br><br>Wishing you many<br>good days ahead ✨',
    eggClicks: ' clicks!',
    eggSecret: '🤫 Secret achievement unlocked',
    back: 'Close',
    login: 'Login', register: 'Sign Up', username: 'Username', password: 'Password', nickname: 'Nickname',
    logout: 'Logout', private: 'Private', setPrivate: 'Set Private', setPublic: 'Set Public',
    myPrivate: 'My Private Posts', save: 'Save', editMsg: 'Edit', deleteMsg: 'Remove',
    deleteConfirm: 'Should we take this memory down?',
    loginOk: 'Welcome ✨', registerOk: 'Signed up ✨', authFail: 'Please try again',
    loginRequiredPopup: 'Login is required for this page. Would you like to login?',
    ok: 'OK',
    profile: 'Profile', changeAvatar: 'Change Photo', changeNickname: 'Change Nickname', phone: 'Phone', email: 'Email', changePwd: 'Change Password', oldPwd: 'Current Password', newPwd: 'New Password', pwdChanged: 'Password changed ✨', profileSaved: 'Saved ✨', loginFirst: 'Please login first',
    timeJustNow: 'now', timeMin: 'm', timeHour: 'h', timeDay: 'd',
    story1: 'A Day ☀️', story2: 'Memories 🌙', story3: 'Ahead 🌸',
    story1Content: 'A nice day\nthe breeze was gentle 🌿',
    story2Content: 'Little moments\nstay in my memory 📖',
    story3Content: 'The stories yet to come\nI want to document them too ✨',
  },
  ja: {
    appTitle: 'diary.', home: 'ホーム', gallery: 'フィード', messages: '掲示板',
    profileBio: 'ささやかな日々の記録 ✦',
    photos: '投稿', msgCount: '件', likes: 'いいね',
    heroLine1: '覚えておきたい瞬間を', heroLine2: 'ここに集めるね',
    ourMoments: '記録', uploadPhoto: '投稿',
    writeCaption: 'キャプションを書いて...',
    cancel: 'キャンセル', uploading: '...', post: '投稿',
    noPhotos: 'まだ写真がありません\n最初の写真を投稿しましょう！',
    noComments: 'まだコメントがありません',
    guestbook: '掲示板', comments: 'コメント',
    yourName: '名前', writeMsg: '書きたいことを書いて...',
    send: '送信', addComment: 'コメントする...',
    noMessages: 'まだメッセージがありません\n最初のメッセージを残しましょう！',
    footer: 'everyday',
    mood_love: '穏やか', mood_happy: '嬉しい', mood_miss: '会いたい', mood_shy: '恥ずかしい', mood_star: '星',
    toastPhotoOk: '投稿完了 📸', toastPhotoFail: '失敗、もう一度',
    toastMsgOk: '投稿完了 ✉️', toastMsgFail: '失敗、もう一度',
    toastCommentOk: 'コメント完了 💬',
    anonymous: '匿名',
    peopleLike: '人がいいねしました',
    viewAllComments: (n) => `コメント${n}件をすべて見る`,
    inMyHeart: 'どこか',
    ago: '前',
    eggTitle: '✦',
    eggText: 'ここまで来てくれてありがとう<br>平凡な日も<br>記録すれば特別になるから<br><br>これからも良い日が<br>たくさんありますように ✨',
    eggClicks: '回クリック!',
    eggSecret: '🤫 秘密の実績達成',
    back: '閉じる',
    login: 'ログイン', register: '新規登録', username: 'ユーザー名', password: 'パスワード', nickname: 'ニックネーム',
    logout: 'ログアウト', private: '非公開', setPrivate: '非公開にする', setPublic: '公開にする',
    myPrivate: '秘密の投稿', save: '保存', editMsg: '編集', deleteMsg: 'しまう',
    deleteConfirm: 'この記憶をしまいますか？',
    loginOk: 'ようこそ ✨', registerOk: '登録完了 ✨', authFail: 'もう一度お試しください',
    loginRequiredPopup: 'このページをご利用いただくにはログインが必要です。ログインしますか？',
    ok: 'はい',
    profile: 'プロフィール', changeAvatar: '写真変更', changeNickname: 'ニックネーム変更', phone: '電話番号', email: 'メール', changePwd: 'パスワード変更', oldPwd: '現在のパスワード', newPwd: '新しいパスワード', pwdChanged: 'パスワードを変更しました ✨', profileSaved: '保存しました ✨', loginFirst: 'ログインしてください',
    timeJustNow: 'たった今', timeMin: '分', timeHour: '時間', timeDay: '日',
    story1: 'ある日 ☀️', story2: '記録 🌙', story3: 'これから 🌸',
    story1Content: '気分のいい一日だった\n風が気持ちよかったよ 🌿',
    story2Content: 'ささやかな瞬間が\nずっと記憶に残ってる 📖',
    story3Content: 'これからの物語も\n記録していきたい ✨',
  },
  zh: {
    appTitle: 'diary.', home: '首页', gallery: '动态', messages: '留言板',
    profileBio: '细碎日常记录 ✦',
    photos: '动态', msgCount: '条留言', likes: '获赞',
    heroLine1: '想把记住的瞬间', heroLine2: '都留在这里',
    ourMoments: '记录', uploadPhoto: '发布',
    writeCaption: '写点什么吧...',
    cancel: '取消', uploading: '...', post: '发布',
    noPhotos: '还没有照片\n发第一条动态吧！',
    noComments: '还没有评论',
    guestbook: '留言板', comments: '评论',
    yourName: '你的名字', writeMsg: '写下你想说的话...',
    send: '发送', addComment: '添加评论...',
    noMessages: '还没有留言\n留第一条吧！',
    footer: 'everyday',
    mood_love: '平静', mood_happy: '开心', mood_miss: '想念', mood_shy: '害羞', mood_star: '星星',
    toastPhotoOk: '发布成功 📸', toastPhotoFail: '失败，请重试',
    toastMsgOk: '留言成功 ✉️', toastMsgFail: '失败，请重试',
    toastCommentOk: '评论成功 💬',
    anonymous: '匿名',
    peopleLike: '人觉得很赞',
    viewAllComments: (n) => `查看全部 ${n} 条评论`,
    inMyHeart: '某处',
    ago: '前',
    eggTitle: '✦',
    eggText: '谢谢你找到这个页面<br>平凡的日子<br>记录下来也会变得特别<br><br>希望你接下来的每一天<br>都顺顺利利的 ✨',
    eggClicks: '次点击！',
    eggSecret: '🤫 秘密成就达成',
    back: '关闭',
    login: '登录', register: '注册', username: '账号', password: '密码', nickname: '昵称',
    logout: '退出登录', private: '私密', setPrivate: '设为私密', setPublic: '设为公开',
    myPrivate: '我的私密记录', save: '保存', editMsg: '编辑', deleteMsg: '收起',
    deleteConfirm: '要把这条记录收起来吗？',
    loginOk: '欢迎 ✨', registerOk: '注册成功 ✨', authFail: '请重试',
    loginRequiredPopup: '该页面需要登录才能访问。是否立即登录？',
    ok: '确定',
    profile: '个人主页', changeAvatar: '更换头像', changeNickname: '修改昵称', phone: '手机号', email: '邮箱', changePwd: '修改密码', oldPwd: '当前密码', newPwd: '新密码', pwdChanged: '密码修改成功 ✨', profileSaved: '保存成功 ✨', loginFirst: '请先登录',
    timeJustNow: '刚刚', timeMin: '分钟', timeHour: '小时', timeDay: '天',
    story1: '某一天 ☀️', story2: '记录 🌙', story3: '以后 🌸',
    story1Content: '心情不错的一天\n风很舒服 🌿',
    story2Content: '细碎的瞬间\n总是留在记忆里 📖',
    story3Content: '以后的故事\n也想继续记录 ✨',
  },
}

function t(key, params) {
  const val = i18n[currentLang.value]?.[key] || i18n['ko']?.[key] || key
  if (typeof val === 'function') return val(...(params || []))
  return val
}

// ============ State ============
const activeSection = ref('home')
const photos = ref([])
const messages = ref([])
const stats = reactive({ photos: 0, messages: 0, total_likes: 0 })
const tapHeart = ref(null)
const photoLikedSet = reactive(new Set())
const msgLikedSet = reactive(new Set())
const userHash = ref(localStorage.getItem('love_user_hash') || 'user_' + Math.random().toString(36).slice(2, 10))

// Auth
const currentUser = ref(null)
const showLoginModal = ref(false)
const showUserMenu = ref(false)
const loginMode = ref('login')
const authUsername = ref('')
const authPassword = ref('')
const authNickname = ref('')
const authError = ref('')
const authLoading = ref(false)
const avatarInput = ref(null)

// Profile edit
const editNickname = ref('')
const editPhone = ref('')
const editEmail = ref('')
const oldPassword = ref('')
const newPassword = ref('')
const savingProfile = ref(false)
const changingPwd = ref(false)
const profileTab = ref('photos')
const profilePhotoModal = ref(null)

// Computed: my content
const myPhotos = ref([])
const myMessages = ref([])

// Login requirement popup
const showLoginRequiredPopup = ref(false)

// Message edit/delete/private
const editingMsgId = ref(null)
const editingMsgContent = ref('')
const msgIsPrivate = ref(false)

// Photo edit/private
const uploadIsPrivate = ref(false)
const editingPhotoId = ref(null)
const editingPhotoCaption = ref('')

// Upload
const showUploadModal = ref(false)
const uploadLocation = ref('')
const uploadFile = ref(null)
const uploadPreview = ref(null)
const uploadCaption = ref('')
const uploading = ref(false)

// Comments
const showCommentsPanel = ref(false)
const currentCommentPhotoId = ref(null)
const commentsList = ref([])
const commentNickname = ref(localStorage.getItem('diary_comment_nickname') || '')
const commentText = ref('')
const editingCommentId = ref(null)
const editingCommentContent = ref('')

// Messages
const msgNickname = ref('')
const msgContent = ref('')
const msgMood = ref('love')

// Easter eggs
const showEggPage = ref(false)
const eggClick = ref(0)
const logoClicks = ref(0)
const showStoryViewer = ref(false)
const viewingStory = reactive({ icon: '', name: '', content: '' })
const currentQuote = ref(0)
const konamiCode = ['ArrowUp','ArrowUp','ArrowDown','ArrowDown','ArrowLeft','ArrowRight','ArrowLeft','ArrowRight','b','a']
const konamiIndex = ref(0)

// Toast
const toast = reactive({ show: false, message: '', type: 'success' })

// Confirm dialog
const confirmDialog = reactive({ show: false, message: '', icon: '', onConfirm: () => {}, onCancel: () => {} })

function showConfirm(message, onConfirm, icon = '🗑️') {
  return new Promise((resolve) => {
    confirmDialog.show = true
    confirmDialog.message = message
    confirmDialog.icon = icon
    confirmDialog.onConfirm = () => {
      confirmDialog.show = false
      onConfirm()
      resolve(true)
    }
    confirmDialog.onCancel = () => {
      confirmDialog.show = false
      resolve(false)
    }
  })
}

// Quote rotation
let quoteInterval = null

// Stories
const stories = ref([
  { id: 1, icon: '☀️', name: 'story', content: '', viewed: false },
  { id: 2, icon: '🌙', name: 'story', content: '', viewed: false },
  { id: 3, icon: '🌸', name: 'story', content: '', viewed: false },
])

// Nav
const navItems = [
  { id: 'home', icon: '🏠' },
  { id: 'profile', icon: '👤' },
  { id: 'gallery', icon: '📷' },
  { id: 'messages', icon: '💬' },
]

// Moods
const moods = [
  { value: 'love', icon: '🌿', key: 'mood_love' },
  { value: 'happy', icon: '😊', key: 'mood_happy' },
  { value: 'miss', icon: '🥺', key: 'mood_miss' },
  { value: 'shy', icon: '🙈', key: 'mood_shy' },
  { value: 'star', icon: '⭐', key: 'mood_star' },
]

// Computed
const gallerySearch = ref('')
const filteredPhotos = computed(() => {
  const q = gallerySearch.value.trim().toLowerCase()
  if (!q) return photos.value
  return photos.value.filter(p =>
    (p.caption && p.caption.toLowerCase().includes(q)) ||
    (p.location && p.location.toLowerCase().includes(q)) ||
    (p.author_name && p.author_name.toLowerCase().includes(q))
  )
})
const msgSearch = ref('')
const filteredMessages = computed(() => {
  const q = msgSearch.value.trim().toLowerCase()
  if (!q) return messages.value
  return messages.value.filter(m =>
    (m.content && m.content.toLowerCase().includes(q)) ||
    (m.nickname && m.nickname.toLowerCase().includes(q))
  )
})

// ============ Auth Functions ============

async function handleAuth() {
  if (!authUsername.value.trim() || !authPassword.value.trim()) {
    authError.value = t('authFail')
    return
  }
  authLoading.value = true
  authError.value = ''
  try {
    const fd = new FormData()
    fd.append('username', authUsername.value.trim())
    fd.append('password', authPassword.value)
    if (loginMode.value === 'register') {
      fd.append('nickname', authNickname.value.trim())
      const res = await api.register(fd)
      if (res.data.code === 200) {
        localStorage.setItem('diary_token', res.data.token)
        currentUser.value = res.data.user
        initProfileEdit()
        showToast(t('registerOk'))
        showLoginModal.value = false
        authUsername.value = ''
        authPassword.value = ''
        authNickname.value = ''
        fetchData()
      } else {
        authError.value = res.data.detail || t('authFail')
      }
    } else {
      const res = await api.login(fd)
      if (res.data.code === 200) {
        localStorage.setItem('diary_token', res.data.token)
        currentUser.value = res.data.user
        initProfileEdit()
        showToast(t('loginOk'))
        showLoginModal.value = false
        authUsername.value = ''
        authPassword.value = ''
        fetchData()
      } else {
        authError.value = res.data.detail || t('authFail')
      }
    }
  } catch (e) {
    authError.value = t('authFail')
  } finally {
    authLoading.value = false
  }
}

function logout() {
  localStorage.removeItem('diary_token')
  currentUser.value = null
  showUserMenu.value = false
  editNickname.value = ''
  editPhone.value = ''
  editEmail.value = ''
  oldPassword.value = ''
  newPassword.value = ''
  showToast(t('logout'))
  fetchData()
}

function initProfileEdit() {
  if (currentUser.value) {
    editNickname.value = currentUser.value.nickname || ''
    editPhone.value = currentUser.value.phone || ''
    editEmail.value = currentUser.value.email || ''
  }
}

async function checkAuth() {
  const token = localStorage.getItem('diary_token')
  if (token) {
    try {
      const res = await api.getMe(token)
      if (res.data.code === 200) {
        currentUser.value = res.data.user
        initProfileEdit()
      } else {
        localStorage.removeItem('diary_token')
      }
    } catch (e) {
      localStorage.removeItem('diary_token')
    }
  }
}

// Handle navigation with login check
function navigateTo(section) {
  // Define which sections require login
  const restrictedSections = ['gallery', 'messages']
  
  // Check if the section requires login and user is not logged in
  if (restrictedSections.includes(section) && !currentUser.value) {
    // Show login required popup first
    showLoginRequiredPopup.value = true
    return false
  }
  
  // If allowed, change the active section
  activeSection.value = section
  return true
}

// Handle login required popup confirmation
function onLoginRequiredConfirm() {
  showLoginRequiredPopup.value = false
  // After user confirms, show login modal
  setTimeout(() => {
    showLoginModal.value = true
  }, 300)
}

// Handle login required popup cancel
function onLoginRequiredCancel() {
  showLoginRequiredPopup.value = false
  // Keep user on home page
  activeSection.value = 'home'
}

function isMsgOwner(msg) {
  return currentUser.value && msg.user_id && msg.user_id === currentUser.value.id
}

function isPhotoOwner(photo) {
  return currentUser.value && photo.user_id && photo.user_id === currentUser.value.id
}

function openPhotoDetail(photo) {
  profilePhotoModal.value = photo
}

function isCommentOwner(comment) {
  return currentUser.value && comment.nickname === (currentUser.value.nickname || currentUser.value.username)
}

function startEditPhoto(photo) {
  editingPhotoId.value = photo.id
  editingPhotoCaption.value = photo.caption || ''
}

async function confirmEditPhoto(photoId) {
  const token = api.getToken()
  if (!token) return
  try {
    const fd = new FormData()
    fd.append('caption', editingPhotoCaption.value)
    fd.append('token', token)
    const res = await api.updatePhoto(photoId, fd)
    if (res.data.code === 200) {
      showToast(t('save'))
      editingPhotoId.value = null
      fetchPhotos()
    }
  } catch (e) {
    showToast(t('authFail'), 'error')
  }
}

async function togglePhotoPrivate(photo) {
  const token = api.getToken()
  if (!token) return
  try {
    const fd = new FormData()
    fd.append('is_private', photo.is_private ? '0' : '1')
    fd.append('token', token)
    const res = await api.updatePhoto(photo.id, fd)
    if (res.data.code === 200) {
      fetchPhotos()
    }
  } catch (e) {}
}

async function handleDeletePhoto(photoId) {
  await showConfirm(t('deleteConfirm'), async () => {
    const token = api.getToken()
    if (!token) return
    try {
      const res = await api.deletePhoto(photoId, token)
      if (res.data.code === 200) {
        fetchPhotos()
        fetchStats()
      }
    } catch (e) {}
  })
}

function startEditMsg(msg) {
  editingMsgId.value = msg.id
  editingMsgContent.value = msg.content
}

async function confirmEditMsg(msgId) {
  if (!editingMsgContent.value.trim()) return
  const token = api.getToken()
  if (!token) return
  try {
    const fd = new FormData()
    fd.append('content', editingMsgContent.value)
    fd.append('token', token)
    const res = await api.updateMessage(msgId, fd)
    if (res.data.code === 200) {
      showToast(t('save'))
      editingMsgId.value = null
      fetchMessages()
    }
  } catch (e) {
    showToast(t('authFail'), 'error')
  }
}

async function toggleMsgPrivate(msg) {
  const token = api.getToken()
  if (!token) return
  try {
    const fd = new FormData()
    fd.append('is_private', msg.is_private ? '0' : '1')
    fd.append('token', token)
    const res = await api.updateMessage(msg.id, fd)
    if (res.data.code === 200) {
      fetchMessages()
    }
  } catch (e) {}
}

async function handleDeleteMsg(msgId) {
  await showConfirm(t('deleteConfirm'), async () => {
    const token = api.getToken()
    if (!token) return
    try {
      const res = await api.deleteMessage(msgId, token)
      if (res.data.code === 200) {
        fetchMessages()
        fetchStats()
      }
    } catch (e) {}
  })
}

// ============ Helpers ============
function getPhotoUrl(filename) {
  return `http://localhost:520/uploads/${filename}`
}

function showToast(message, type = 'success') {
  toast.message = message
  toast.type = type
  toast.show = true
  setTimeout(() => { toast.show = false }, 2500)
}

function formatTimeAgo(dateStr) {
  if (!dateStr) return ''
  const now = new Date()
  const d = new Date(dateStr)
  const diff = Math.floor((now - d) / 1000)
  if (diff < 60) return t('timeJustNow')
  if (diff < 3600) return Math.floor(diff / 60) + t('timeMin') + t('ago')
  if (diff < 86400) return Math.floor(diff / 3600) + t('timeHour') + t('ago')
  return Math.floor(diff / 86400) + t('timeDay') + t('ago')
}

// ============ Features ============

// Double tap to like
function doubleTapLike(photo, event) {
  tapHeart.value = photo.id
  setTimeout(() => { tapHeart.value = null }, 800)
  if (!photoLikedSet.has(photo.id)) {
    togglePhotoLike(photo)
  }
}

// Toggle photo like
async function togglePhotoLike(photo) {
  try {
    const res = await api.likePhoto(photo.id, userHash.value)
    if (res.data.code === 200) {
      if (res.data.liked) {
        photoLikedSet.add(photo.id)
      } else {
        photoLikedSet.delete(photo.id)
      }
      photo.likes = res.data.likes
    }
  } catch (e) { console.error(e) }
}

// Toggle message like
async function toggleMsgLike(msg) {
  try {
    const res = await api.likeMessage(msg.id, userHash.value)
    if (res.data.code === 200) {
      if (res.data.liked) {
        msgLikedSet.add(msg.id)
        msg.likes = (msg.likes || 0) + 1
      } else {
        msgLikedSet.delete(msg.id)
        msg.likes = Math.max(0, (msg.likes || 0) - 1)
      }
    }
  } catch (e) { console.error(e) }
}

// Open comments panel
async function openComments(photo) {
  currentCommentPhotoId.value = photo.id
  showCommentsPanel.value = true
  try {
    const res = await api.getComments(photo.id)
    if (res.data.code === 200) commentsList.value = res.data.data
  } catch (e) { console.error(e) }
}

// Quick comment (inline)
async function quickComment(photo, event) {
  const input = event.target.closest('.post-comment-input')?.querySelector('.quick-comment')
  if (!input || !input.value.trim()) return
  try {
    const fd = new FormData()
    const nickname = currentUser.value ? (currentUser.value.nickname || currentUser.value.username) : (commentNickname.value || t('anonymous'))
    fd.append('nickname', nickname)
    if (!currentUser.value && commentNickname.value) {
      localStorage.setItem('diary_comment_nickname', commentNickname.value)
    }
    fd.append('content', input.value.trim())
    const res = await api.addComment(photo.id, fd)
    if (res.data.code === 200) {
      showToast(t('toastCommentOk'))
      input.value = ''
      photo.comments_count = (photo.comments_count || 0) + 1
      fetchPhotos()
    }
  } catch (e) {
    showToast(t('toastMsgFail'), 'error')
  }
}

// Submit comment (panel)
async function submitComment() {
  if (!commentText.value.trim() || !currentCommentPhotoId.value) return
  try {
    const fd = new FormData()
    const nickname = currentUser.value ? (currentUser.value.nickname || currentUser.value.username) : (commentNickname.value || t('anonymous'))
    fd.append('nickname', nickname)
    if (!currentUser.value && commentNickname.value) {
      localStorage.setItem('diary_comment_nickname', commentNickname.value)
    }
    fd.append('content', commentText.value.trim())
    const res = await api.addComment(currentCommentPhotoId.value, fd)
    if (res.data.code === 200) {
      showToast(t('toastCommentOk'))
      commentText.value = ''
      openComments({ id: currentCommentPhotoId.value })
      fetchPhotos()
    }
  } catch (e) {
    showToast(t('toastMsgFail'), 'error')
  }
}

function startEditComment(comment) {
  editingCommentId.value = comment.id
  editingCommentContent.value = comment.content
}

async function confirmEditComment(commentId) {
  if (!editingCommentContent.value.trim()) return
  const token = api.getToken()
  if (!token) return
  try {
    const fd = new FormData()
    fd.append('content', editingCommentContent.value.trim())
    fd.append('token', token)
    const res = await api.updateComment(commentId, fd)
    if (res.data.code === 200) {
      showToast(t('save'))
      editingCommentId.value = null
      openComments({ id: currentCommentPhotoId.value })
      fetchPhotos()
    }
  } catch (e) {
    showToast(t('authFail'), 'error')
  }
}

async function handleDeleteComment(commentId) {
  await showConfirm(t('deleteConfirm'), async () => {
    const token = api.getToken()
    if (!token) return
    try {
      const res = await api.deleteComment(commentId, token)
      if (res.data.code === 200) {
        showToast('Deleted')
        openComments({ id: currentCommentPhotoId.value })
        fetchPhotos()
        fetchStats()
      }
    } catch (e) {
      showToast(t('authFail'), 'error')
    }
  })
}

// Upload
function onFileSelect(e) {
  const file = e.target.files[0]
  if (!file) return
  uploadFile.value = file
  uploadPreview.value = URL.createObjectURL(file)
  uploadCaption.value = ''
  uploadIsPrivate.value = false
  uploadLocation.value = ''
  showUploadModal.value = true
  fetchLocation()
  e.target.value = ''
}

async function fetchLocation() {
  if (!navigator.geolocation) return
  try {
    const pos = await new Promise((resolve, reject) =>
      navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 8000 })
    )
    const { latitude, longitude } = pos.coords
    const res = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json&accept-language=${currentLang.value}`)
    const data = await res.json()
    if (data.address) {
      const a = data.address
      const name = a.city || a.town || a.village || a.county || a.state || ''
      const country = a.country || ''
      uploadLocation.value = name && country ? `${name}, ${country}` : (name || country || '')
    }
  } catch (e) {
    // silently ignore location errors
  }
}

async function confirmUpload() {
  if (!uploadFile.value) return
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', uploadFile.value)
    fd.append('caption', uploadCaption.value)
    if (uploadLocation.value) fd.append('location', uploadLocation.value)
    const token = api.getToken()
    if (token) fd.append('token', token)
    if (currentUser.value && uploadIsPrivate.value) fd.append('is_private', '1')
    const res = await api.uploadPhoto(fd)
    if (res.data.code === 200) {
      showToast(t('toastPhotoOk'))
      showUploadModal.value = false
      uploadFile.value = null
      uploadPreview.value = null
      uploadIsPrivate.value = false
      fetchPhotos()
      fetchStats()
    }
  } catch (e) {
    showToast(t('toastPhotoFail'), 'error')
  } finally {
    uploading.value = false
  }
}

// Avatar upload
async function handleAvatarUpload(e) {
  const file = e.target.files?.[0]
  if (!file) return
  try {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('token', api.getToken())
    const res = await api.uploadAvatar(fd)
    if (res.data.code === 200) {
      currentUser.value = { ...currentUser.value, avatar: res.data.filename }
      showToast('✓')
    }
  } catch (e) {
    showToast('✗', 'error')
  }
  e.target.value = ''
}

async function saveProfile() {
  savingProfile.value = true
  try {
    const fd = new FormData()
    fd.append('token', api.getToken())
    fd.append('nickname', editNickname.value)
    fd.append('phone', editPhone.value)
    fd.append('email', editEmail.value)
    const res = await api.updateProfile(fd)
    if (res.data.code === 200) {
      currentUser.value = { ...currentUser.value, ...res.data.user }
      showToast(t('profileSaved'))
    }
  } catch (e) {
    showToast(t('authFail'), 'error')
  } finally {
    savingProfile.value = false
  }
}

async function changePassword() {
  if (!oldPassword.value || !newPassword.value) return
  changingPwd.value = true
  try {
    const fd = new FormData()
    fd.append('token', api.getToken())
    fd.append('old_password', oldPassword.value)
    fd.append('new_password', newPassword.value)
    const res = await api.changePassword(fd)
    if (res.data.code === 200) {
      showToast(t('pwdChanged'))
      oldPassword.value = ''
      newPassword.value = ''
    }
  } catch (e) {
    showToast(e.response?.data?.detail || t('authFail'), 'error')
  } finally {
    changingPwd.value = false
  }
}

// Avatar helpers
const UPLOAD_BASE = 'http://localhost:520/uploads/'
function getAvatarUrl(avatar) {
  return avatar ? (UPLOAD_BASE + avatar) : null
}
function getAvatarStyle(user) {
  if (user?.avatar) {
    return {
      backgroundImage: `url(${UPLOAD_BASE}${user.avatar})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    }
  }
  return {}
}

// Submit message
async function submitMessage() {
  if (!msgContent.value.trim()) return
  try {
    const fd = new FormData()
    const token = api.getToken()
    if (token) fd.append('token', token)
    fd.append('nickname', currentUser.value ? (currentUser.value.nickname || currentUser.value.username) : (msgNickname.value || t('anonymous')))
    fd.append('content', msgContent.value)
    fd.append('mood', msgMood.value)
    if (currentUser.value && msgIsPrivate.value) fd.append('is_private', '1')
    const res = await api.createMessage(fd)
    if (res.data.code === 200) {
      showToast(t('toastMsgOk'))
      msgContent.value = ''
      msgIsPrivate.value = false
      fetchMessages()
      fetchStats()
    }
  } catch (e) {
    showToast(t('toastMsgFail'), 'error')
  }
}

// Easter eggs — hidden triggers
function checkLogoEgg() {
  if (logoClicks.value >= 7) {
    showEggPage.value = true
    eggClick.value = 0
    logoClicks.value = 0
  }
}

function miniEgg() {
  if (activeSection.value === 'home') {
    document.body.style.transform = 'scale(0.95)'
    setTimeout(() => { document.body.style.transform = '' }, 300)
  }
}

function bookmarkEgg() {
  showToast('🔖 ' + (currentLang.value === 'ko' ? '저장됨!' : 'Saved!'))
}

function quoteEgg() {
  currentQuote.value = (currentQuote.value + 1) % 3
}

function viewStory(s) {
  s.viewed = true
  viewingStory.icon = s.icon
  viewingStory.name = s.name
  const lang = currentLang.value
  const key = `story${s.id}Content`
  viewingStory.content = i18n[lang]?.[key] || i18n['ko']?.[key] || ''
  showStoryViewer.value = true
  setTimeout(() => { showStoryViewer.value = false }, 4000)
}

// Konami code listener
function onKeyDown(e) {
  if (konamiCode[konamiIndex.value] === e.key) {
    konamiIndex.value++
    if (konamiIndex.value === konamiCode.length) {
      konamiIndex.value = 0
      showEggPage.value = true
      eggClick.value = 20
    }
  } else {
    konamiIndex.value = 0
  }
}

function onGlobalClick(e) {
  // Secret: click 7 times on empty area to unlock
}

// Decorative styles
function petalStyle(i) {
  return {
    left: Math.random() * 100 + '%',
    animationDelay: Math.random() * 10 + 's',
    animationDuration: (8 + Math.random() * 12) + 's',
    fontSize: (8 + Math.random() * 14) + 'px',
    opacity: 0.15 + Math.random() * 0.2,
  }
}

function eggFloatStyle(i) {
  return {
    left: Math.random() * 100 + '%',
    animationDelay: Math.random() * 5 + 's',
    animationDuration: (4 + Math.random() * 6) + 's',
    fontSize: (12 + Math.random() * 20) + 'px',
  }
}

// ============ Fetch ============
async function fetchPhotos() {
  try {
    const token = api.getToken()
    const res = await api.getPhotos(token)
    if (res.data.code === 200) {
      photos.value = res.data.data
      photos.value.forEach(p => {
        if (p.likes > 0) photoLikedSet.add(p.id)
      })
    }
  } catch (e) { console.error(e) }
  fetchMyContent()
}

async function fetchMessages() {
  try {
    const token = api.getToken()
    const res = await api.getMessages(token)
    if (res.data.code === 200) messages.value = res.data.data
  } catch (e) { console.error(e) }
  fetchMyContent()
}

async function fetchStats() {
  try {
    const res = await api.getStats()
    if (res.data.code === 200) Object.assign(stats, res.data.data)
  } catch (e) {}
}

function fetchData() {
  fetchPhotos()
  fetchMessages()
  fetchStats()
}

async function fetchMyContent() {
  const token = api.getToken()
  if (!token) return
  try {
    const [photoRes, msgRes] = await Promise.all([
      api.getMyPhotos(token),
      api.getMyMessages(token)
    ])
    if (photoRes.data.code === 200) myPhotos.value = photoRes.data.data
    if (msgRes.data.code === 200) myMessages.value = msgRes.data.data
  } catch (e) { console.error(e) }
}

// ============ Lifecycle ============
onMounted(() => {
  localStorage.setItem('love_user_hash', userHash.value)
  checkAuth().then(() => { fetchData(); fetchMyContent() })
  window.addEventListener('keydown', onKeyDown)
  quoteInterval = setInterval(() => {
    currentQuote.value = (currentQuote.value + 1) % 3
  }, 5000)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeyDown)
  if (quoteInterval) clearInterval(quoteInterval)
})
</script>

<style>
/* ============ RESET ============ */
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#fafafa;--bg-card:#ffffff;--text:#262626;--text-light:#8e8e8e;
  --accent:#0095f6;--accent-light:#e8f5fd;--accent-soft:#d4edfc;
  --accent-deep:#0081d6;--gradient-soft:linear-gradient(135deg, #f5f5f5 0%, #eeeeee 50%, #f0f0f0 100%);
  --gradient-accent:linear-gradient(135deg, #0095f6, #00b4d8);
  --border:#dbdbdb;--border-light:#efefef;
  --shadow:0 1px 8px rgba(0,0,0,0.08);
  --shadow-md:0 2px 16px rgba(0,0,0,0.1);
  --shadow-lg:0 8px 40px rgba(0,0,0,0.15);
  --radius:12px;--radius-sm:8px;--radius-lg:16px;
  --transition:0.2s cubic-bezier(0.4,0,0.2,1);
}
html{scroll-behavior:smooth;-webkit-tap-highlight-color:transparent}
body{
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans KR',Roboto,sans-serif;
  background:var(--bg);color:var(--text);line-height:1.5;min-height:100vh;overflow-x:hidden;
  transition:transform 0.3s ease;
  -webkit-font-smoothing:antialiased;
}
.app{max-width:480px;margin:0 auto;min-height:100vh;position:relative;background:var(--bg)}

/* ============ FLOATING PARTICLES ============ */
.petals{position:fixed;inset:0;pointer-events:none;z-index:0;overflow:hidden}
.petal{position:absolute;bottom:-30px;animation:float-up linear infinite;font-size:10px;opacity:0.08}
@keyframes float-up{
  0%{transform:translateY(0) rotate(0) translateX(0);opacity:0}
  10%{opacity:var(--o,0.08)}
  50%{transform:translateY(-50vh) rotate(180deg) translateX(20px)}
  90%{opacity:var(--o,0.08)}
  100%{transform:translateY(-110vh) rotate(360deg) translateX(-15px);opacity:0}
}

/* ============ HEADER ============ */
.header{
  position:sticky;top:0;z-index:10;
  background:rgba(250,250,250,0.95);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border-bottom:1px solid var(--border-light);
}
.header-inner{display:flex;align-items:center;justify-content:space-between;padding:12px 16px}
.logo{display:flex;align-items:center;cursor:pointer;user-select:none;transition:transform 0.2s ease}
.logo:hover{transform:scale(1.02)}
.logo-img{height:28px;width:auto}
.header-actions{display:flex;align-items:center;gap:12px}

/* Login trigger */
.login-trigger{border:none;background:transparent;cursor:pointer;padding:4px;border-radius:50%;transition:transform 0.2s ease}
.login-trigger:hover{transform:scale(1.08)}
.login-icon{
  width:32px;height:32px;border-radius:50%;background:#f0f0f0;
  display:flex;align-items:center;justify-content:center;font-size:14px;
  transition:all 0.2s ease;
}
.login-icon:hover{background:#e8e8e8}
.login-icon.logged{
  background:var(--accent);color:#fff;font-weight:600;font-size:12px;
  box-shadow:0 2px 8px rgba(0,149,246,0.3);
}
.user-menu{position:relative}

/* User dropdown */
.user-dropdown{
  position:absolute;top:40px;right:0;z-index:200;
  background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);
  box-shadow:var(--shadow-lg);padding:6px 0;min-width:180px;
  animation:dropdownIn 0.15s ease;
}
@keyframes dropdownIn{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:translateY(0)}}
.ud-name{padding:12px 16px 8px;font-size:14px;font-weight:600;color:var(--text);border-bottom:1px solid var(--border-light);margin-bottom:4px}
.ud-item{
  display:block;width:100%;padding:10px 16px;border:none;background:transparent;
  font-size:14px;text-align:left;cursor:pointer;font-family:inherit;color:var(--text);
  transition:all 0.15s ease;
}
.ud-item:hover{background:var(--bg)}
.ud-logout{color:#ed4956;border-top:1px solid var(--border-light);margin-top:4px;padding-top:12px}

/* Login modal */
.login-modal{
  background:var(--bg-card);border-radius:var(--radius-lg);padding:28px 24px;width:100%;max-width:360px;
  box-shadow:var(--shadow-lg);border:none;
  animation:modalIn 0.2s ease;
}
@keyframes modalIn{from{opacity:0;transform:scale(0.96) translateY(8px)}to{opacity:1;transform:scale(1) translateY(0)}}
.login-tabs{display:flex;margin-bottom:20px;gap:0;background:var(--bg);padding:3px;border-radius:10px}
.login-tab{
  flex:1;padding:10px;border:none;background:transparent;font-size:14px;
  cursor:pointer;font-family:inherit;color:var(--text-light);transition:var(--transition);
  border-radius:8px;
}
.login-tab.active{background:var(--bg-card);color:var(--text);font-weight:600;box-shadow:0 1px 4px rgba(0,0,0,0.08)}
.auth-error{font-size:12px;color:#ed4956;margin-bottom:12px;text-align:center;padding:8px 12px;background:#fff5f5;border-radius:8px}

/* Language */
.lang-switcher{display:flex;gap:1px;background:var(--bg);border-radius:8px;padding:2px;border:1px solid var(--border-light)}
.lang-btn{
  padding:5px 10px;border:none;background:transparent;border-radius:6px;
  font-size:11px;font-family:inherit;cursor:pointer;color:var(--text-light);
  transition:var(--transition);white-space:nowrap;font-weight:500;
}
.lang-btn.active{background:var(--accent);color:#fff}

/* ============ BOTTOM NAV ============ */
.bottom-nav{
  position:fixed;bottom:0;left:50%;transform:translateX(-50%);
  width:100%;max-width:480px;z-index:10;
  background:rgba(255,255,255,0.98);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border-top:1px solid var(--border-light);
  display:flex;justify-content:space-around;padding:8px 0 env(safe-area-inset-bottom,8px);
}
.bnav-btn{
  display:flex;flex-direction:column;align-items:center;gap:2px;
  padding:6px 16px;border:none;background:transparent;cursor:pointer;
  color:var(--text-light);transition:all 0.15s ease;font-family:inherit;
}
.bnav-btn:hover{opacity:0.7}
.bnav-btn.active .bnav-icon{transform:scale(1)}
.bnav-btn.active .bnav-label{color:var(--text);font-weight:600}
.bnav-icon{font-size:22px;transition:all 0.15s ease}
.bnav-label{font-size:10px;letter-spacing:0.3px}

/* ============ MAIN ============ */
.main{padding:0 0 20px;position:relative;z-index:1}
.section{animation:fadeIn 0.25s ease}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}

/* ============ PROFILE HEADER ============ */
.profile-header{display:flex;align-items:center;gap:16px;padding:20px 16px 16px}
.profile-avatar-wrap{position:relative;flex-shrink:0}
.profile-avatar{
  width:72px;height:72px;border-radius:50%;
  background:#f0f0f0;
  display:flex;align-items:center;justify-content:center;font-size:28px;
  cursor:pointer;transition:all 0.2s ease;z-index:2;position:relative;
}
.profile-avatar:hover{opacity:0.85}
.profile-avatar .avatar-edit-hint{
  position:absolute;bottom:0;right:0;
  width:22px;height:22px;border-radius:50%;
  background:var(--accent);color:#fff;
  font-size:11px;display:flex;align-items:center;justify-content:center;
  opacity:0;transition:opacity 0.2s;
}
.profile-avatar:hover .avatar-edit-hint{opacity:1}
.profile-avatar.no-avatar{cursor:default}
.avatar-ring{
  position:absolute;inset:-3px;border-radius:50%;
  border:2px solid var(--border);
  pointer-events:none;
}
@keyframes ring-rotate{to{filter:none}}
.profile-info{flex:1;min-width:0}
.profile-name{font-size:20px;font-weight:600;margin-bottom:2px;letter-spacing:-0.3px}
.profile-bio{font-size:14px;color:var(--text-light);font-weight:400}

/* Stats */
.profile-stats{
  display:flex;align-items:center;justify-content:space-around;
  padding:14px 20px;margin:0 16px;
  background:transparent;
}
.pstat{text-align:center;cursor:pointer;transition:all 0.15s ease;padding:4px 8px}
.pstat:active{opacity:0.6}
.pstat-num{display:block;font-size:18px;font-weight:700;color:var(--text)}
.pstat-label{font-size:12px;color:var(--text-light);margin-top:0}
.pstat-divider{width:1px;height:28px;background:var(--border)}

/* ============ PROFILE FORM ============ */
.profile-login-required{text-align:center;padding:60px 20px}
.profile-login-required p{color:var(--text-light);margin-bottom:20px;font-size:14px}
.profile-form{padding:20px;max-width:480px;margin:0 auto}
.pf-avatar-section{display:flex;flex-direction:column;align-items:center;gap:12px;margin-bottom:28px}
.pf-avatar-preview{width:100px;height:100px;border-radius:50%;background:#f0f0f0;display:flex;align-items:center;justify-content:center;font-size:40px;background-size:cover;background-position:center}
.pf-avatar-btn{font-size:13px;padding:8px 20px}
.pf-field{margin-bottom:20px}
.pf-label{font-size:12px;color:var(--text-light);margin-bottom:6px;display:block}
.pf-value{font-size:15px;color:var(--text);padding:10px 14px;background:var(--bg-card);border-radius:var(--radius-sm);border:1px solid var(--border-light)}
.pf-input{width:100%;padding:10px 12px;border:1px solid var(--border);border-radius:var(--radius-sm);background:var(--bg);font-size:14px;color:var(--text);transition:border-color 0.15s;box-sizing:border-box}
.pf-input:focus{outline:none;border-color:var(--text)}
.pf-save-btn{width:100%;margin-top:8px;padding:14px}
.pf-divider{height:1px;background:var(--border-light);margin:28px 0}
.pf-section-title{font-size:16px;font-weight:600;margin-bottom:16px;color:var(--text)}
.profile-tabs{display:flex;padding:0 16px;gap:0;margin-bottom:16px;border-bottom:1px solid var(--border-light)}
.ptab{flex:1;padding:12px 0;border:none;background:transparent;border-bottom:2px solid transparent;font-size:14px;font-weight:400;color:var(--text-light);cursor:pointer;transition:all 0.15s;text-align:center}
.ptab.active{color:var(--text);font-weight:600;border-bottom-color:var(--text)}
.profile-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:2px;padding:0}
.pg-item{aspect-ratio:1;overflow:hidden;cursor:pointer}
.pg-item img{width:100%;height:100%;object-fit:cover;transition:opacity 0.2s}
.pg-item:hover img{opacity:0.8}
.profile-empty{text-align:center;padding:40px 20px;color:var(--text-light);font-size:14px}
.lg-avatar{width:80px;height:80px;font-size:32px}
.lg-avatar:hover .avatar-edit-hint{opacity:1}

/* Profile Photo Modal */
.ppm-wrap{background:var(--bg-card);border-radius:0;overflow:hidden;max-width:480px;width:100vw;max-height:90vh;display:flex;flex-direction:column}
.ppm-close{position:absolute;top:12px;right:12px;width:32px;height:32px;border-radius:50%;background:rgba(0,0,0,0.4);color:#fff;border:none;font-size:18px;cursor:pointer;display:flex;align-items:center;justify-content:center;z-index:10}
.ppm-close:hover{background:rgba(0,0,0,0.6)}
.ppm-img{width:100%;max-height:60vh;object-fit:contain;background:#000}
.ppm-info{padding:14px 16px}
.ppm-header{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.ppm-author{font-weight:600;font-size:14px}
.ppm-location{font-size:12px;color:var(--text-light)}
.ppm-caption{font-size:14px;line-height:1.4;margin-bottom:10px}
.ppm-stats{font-size:13px;color:var(--text-light);display:flex;gap:16px}
.ppm-actions{display:flex;gap:8px;margin-top:10px}
.ppm-btn{padding:7px 14px;border-radius:8px;border:1px solid var(--border);background:var(--bg);cursor:pointer;font-size:13px;transition:all 0.15s;font-family:inherit}
.ppm-btn:hover{background:var(--border-light)}
.ppm-delete:hover{background:#fff0f0;border-color:#ed4956;color:#ed4956}
.sm-avatar{width:32px;height:32px}

/* ============ STORIES ============ */
.stories-bar{display:flex;gap:12px;padding:16px;overflow-x:auto;-webkit-overflow-scrolling:touch;scroll-snap-type:x mandatory}
.stories-bar::-webkit-scrollbar{display:none}
.story-item{display:flex;flex-direction:column;align-items:center;gap:6px;cursor:pointer;flex-shrink:0;scroll-snap-align:start;transition:transform 0.15s ease}
.story-item:hover{transform:scale(1.03)}
.story-ring{padding:3px;border-radius:50%;background:linear-gradient(135deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888)}
.story-item.viewed .story-ring{background:var(--border)}
.story-thumb{width:56px;height:56px;border-radius:50%;background:var(--bg);display:flex;align-items:center;justify-content:center;font-size:24px;border:2px solid var(--bg-card)}
.story-name{font-size:11px;color:var(--text-light);max-width:58px;text-align:center;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}

/* ============ FEATURE CARD ============ */
.feature-card{
  margin:0 16px 20px;padding:24px;
  background:var(--bg-card);
  border-radius:var(--radius-lg);cursor:pointer;
  transition:all 0.2s ease;position:relative;overflow:hidden;
  border:1px solid var(--border-light);
  box-shadow:none;
}
.feature-card::before{display:none}
.feature-card:hover{box-shadow:var(--shadow)}
.feature-card:active{transform:scale(0.98)}
.feature-icon{font-size:28px;margin-bottom:12px}
.feature-text{font-size:15px;line-height:1.6;margin-bottom:4px;color:var(--text)}
.feature-text.accent{color:var(--text);font-weight:600;font-size:17px}
.feature-dots{display:flex;gap:6px;margin-top:16px;justify-content:center}
.dot{width:6px;height:6px;border-radius:50%;background:var(--border);transition:all 0.2s ease}
.dot.active{background:var(--accent);width:18px;border-radius:3px}

/* ============ SECTION HEAD ============ */
.section-head{display:flex;align-items:center;justify-content:space-between;padding:16px 16px 12px}
.section-head-actions{display:flex;align-items:center;gap:8px}
.inline-search{
  width:120px;padding:8px 14px;border:1px solid var(--border);border-radius:10px;
  font-size:13px;font-family:inherit;background:var(--bg);color:var(--text);outline:none;
  transition:all 0.2s ease;
}
.inline-search:focus{width:160px;border-color:var(--text)}
.inline-search::placeholder{color:var(--text-light)}
.section-title{font-size:18px;font-weight:700;letter-spacing:-0.2px}
.msg-badge{
  background:var(--accent);color:#fff;font-size:12px;
  padding:4px 10px;border-radius:10px;font-weight:600;
}

/* Upload */
.upload-btn{
  width:34px;height:34px;display:flex;align-items:center;justify-content:center;
  background:transparent;border:1px solid var(--border);border-radius:10px;
  cursor:pointer;transition:all 0.15s ease;
}
.upload-btn:hover{border-color:var(--text-light)}
.upload-btn:active{transform:scale(0.92)}
.upload-icon{font-size:20px;font-weight:300;color:var(--text)}
.upload-location{font-size:12px;color:var(--text-light);margin:-8px 0 12px;display:flex;align-items:center;gap:4px}

/* ============ INSTAGRAM FEED ============ */
.feed{padding:0 0 24px}
.post-card{
  background:var(--bg-card);border:none;
  margin:0 0 8px;
  border-radius:0;box-shadow:none;overflow:hidden;
  border-bottom:1px solid var(--border-light);
}
.post-card.post-private{border-left:none}
.post-header{display:flex;align-items:center;gap:10px;padding:10px 16px}
.post-avatar{
  width:32px;height:32px;border-radius:50%;background:#f0f0f0;
  display:flex;align-items:center;justify-content:center;font-size:14px;
  background-size:cover;background-position:center;flex-shrink:0;
}
.post-avatar.no-avatar-text span{display:none}
.post-user-info{flex:1;min-width:0}
.post-username{font-size:13px;font-weight:600}
.post-location{font-size:11px;color:var(--text-light);margin-left:4px}
.post-private-badge{margin-left:4px}

/* Post owner actions */
.post-owner-actions{display:flex;gap:2px}
.post-action-sm{border:none;background:transparent;font-size:13px;cursor:pointer;padding:4px;opacity:0.5;transition:all 0.15s ease;border-radius:6px}
.post-action-sm:hover{opacity:1;background:var(--bg)}
.photo-edit-wrap{background:var(--bg);padding:10px 0}

/* Post image */
.post-image-wrap{position:relative;width:100%;aspect-ratio:1;overflow:hidden;background:#fafafa}
.post-image-wrap img{width:100%;height:100%;object-fit:cover}

/* Double tap animation */
.double-tap-heart{
  position:absolute;top:50%;left:50%;
  transform:translate(-50%,-50%) scale(0);
  font-size:80px;filter:drop-shadow(0 2px 8px rgba(0,0,0,0.2));
  pointer-events:none;
}
.heart-pop-enter-active{animation:heartPop 0.8s ease forwards}
@keyframes heartPop{
  0%{transform:translate(-50%,-50%) scale(0);opacity:1}
  15%{transform:translate(-50%,-50%) scale(1.2);opacity:1}
  30%{transform:translate(-50%,-50%) scale(0.95);opacity:1}
  80%{transform:translate(-50%,-50%) scale(1);opacity:1}
  100%{transform:translate(-50%,-50%) scale(1.1);opacity:0}
}

/* Post actions */
.post-actions{display:flex;align-items:center;justify-content:space-between;padding:8px 16px 4px}
.post-actions-left{display:flex;gap:14px}
.action-btn{border:none;background:transparent;font-size:22px;cursor:pointer;padding:2px;transition:all 0.15s ease;line-height:1}
.action-btn:hover{opacity:0.6}
.action-btn:active{transform:scale(0.85)}
.action-btn.liked{animation:likePop 0.3s ease}
@keyframes likePop{0%{transform:scale(1)}50%{transform:scale(1.25)}100%{transform:scale(1)}}

/* Post details */
.post-likes{padding:0 16px 4px;font-size:13px;font-weight:600}
.post-caption{padding:0 16px 4px;font-size:13px;line-height:1.5}
.post-caption strong{font-weight:600}
.post-view-comments{padding:2px 16px;font-size:13px;color:var(--text-light);cursor:pointer}
.post-recent-comments{padding:2px 16px 4px;font-size:13px}
.post-comment-item{margin-bottom:2px;line-height:1.4}
.post-comment-item strong{font-weight:600}

/* Quick comment */
.post-comment-input{display:flex;align-items:center;gap:8px;padding:8px 16px 12px;border-top:1px solid var(--border-light)}
.quick-comment{flex:1;border:none;background:transparent;font-size:13px;font-family:inherit;color:var(--text);outline:none}
.quick-comment::placeholder{color:var(--text-light)}
.comment-send{border:none;background:transparent;font-size:13px;font-weight:600;color:var(--accent);cursor:pointer;font-family:inherit;padding:4px 6px}
.post-time{padding:2px 16px 12px;font-size:10px;color:var(--text-light);letter-spacing:0.3px;text-transform:uppercase}

/* ============ UPLOAD MODAL ============ */
.modal-overlay{position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,0.65);display:flex;align-items:center;justify-content:center;padding:70px 20px 80px;animation:fadeIn 0.2s;overflow-y:auto}
.modal{background:var(--bg-card);border-radius:var(--radius-lg);padding:20px;width:100%;max-width:360px;box-shadow:var(--shadow-lg);animation:modalPop 0.2s ease}
@keyframes modalPop{from{opacity:0;transform:scale(0.95)}to{opacity:1;transform:scale(1)}}
.modal-preview{width:100%;aspect-ratio:1;border-radius:var(--radius-sm);overflow:hidden;margin-bottom:14px}
.modal-preview img{width:100%;height:100%;object-fit:cover}
.modal-input{
  width:100%;padding:10px 14px;border:1px solid var(--border);border-radius:var(--radius-sm);
  font-size:14px;font-family:inherit;background:var(--bg);color:var(--text);outline:none;
  transition:all 0.15s ease;margin-bottom:12px;
}
.modal-input:focus{border-color:var(--text)}
.modal-input::placeholder{color:var(--text-light)}
.modal-actions{display:flex;gap:10px}
.btn-cancel,.btn-confirm{flex:1;padding:10px;border:none;border-radius:var(--radius-sm);font-size:14px;cursor:pointer;font-family:inherit;transition:all 0.15s ease;font-weight:600}
.btn-cancel{background:transparent;color:var(--text-light)}
.btn-cancel:hover{color:var(--text)}
.btn-confirm{background:var(--accent);color:#fff}
.btn-confirm:hover:not(:disabled){opacity:0.9}
.btn-confirm:disabled{opacity:0.4;cursor:not-allowed}

/* ============ COMMENTS PANEL ============ */
.comments-panel{position:fixed;inset:0;z-index:9998;background:var(--bg);display:flex;flex-direction:column}
.cp-header{display:flex;align-items:center;justify-content:space-between;padding:14px 16px;border-bottom:1px solid var(--border-light);background:var(--bg-card)}
.cp-back,.cp-close{border:none;background:transparent;font-size:18px;cursor:pointer;padding:6px 8px;border-radius:8px;transition:all 0.15s ease;color:var(--text)}
.cp-back:hover,.cp-close:hover{background:var(--bg)}
.cp-title{font-size:16px;font-weight:600}
.cp-list{flex:1;overflow-y:auto;padding:16px}
.cp-item{display:flex;gap:12px;margin-bottom:16px}
.cp-avatar{
  width:32px;height:32px;border-radius:50%;background:#f0f0f0;color:var(--text-light);
  display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600;flex-shrink:0;
  background-size:cover;background-position:center;
}
.cp-avatar.no-avatar-text span{display:none}
.cp-body{flex:1;min-width:0}
.cp-meta{display:flex;align-items:center;gap:8px;margin-bottom:3px;flex-wrap:wrap}
.cp-meta strong{font-size:13px;font-weight:600}
.cp-time{font-size:11px;color:var(--text-light)}
.cp-body p{font-size:13px;line-height:1.5;color:var(--text)}
.cp-actions{display:flex;gap:2px;margin-left:auto}
.cp-action-btn{border:none;background:transparent;font-size:11px;cursor:pointer;padding:4px;opacity:0.4;transition:all 0.15s ease;border-radius:4px}
.cp-action-btn:hover{opacity:1;background:var(--bg)}
.cp-delete:hover{color:#ed4956}
.cp-edit-wrap{margin-top:6px}
.cp-edit-input{width:100%;padding:8px 10px;border:1px solid var(--border);border-radius:6px;font-size:13px;font-family:inherit;background:var(--bg);color:var(--text);outline:none;margin-bottom:6px}
.cp-edit-input:focus{border-color:var(--text)}
.cp-edit-actions{display:flex;gap:6px;justify-content:flex-end}
.cp-empty{text-align:center;padding:60px 0;color:var(--text-light);font-size:14px}
.cp-input-bar{display:flex;gap:8px;padding:12px 16px;border-top:1px solid var(--border-light);background:var(--bg-card)}
.cp-name{width:70px;padding:8px 10px;border:1px solid var(--border);border-radius:var(--radius-sm);font-size:13px;font-family:inherit;background:var(--bg);color:var(--text);outline:none}
.cp-input{flex:1;padding:8px 12px;border:1px solid var(--border);border-radius:var(--radius-sm);font-size:13px;font-family:inherit;background:var(--bg);color:var(--text);outline:none}
.cp-input:focus,.cp-name:focus{border-color:var(--text)}
.cp-send{border:none;background:var(--accent);color:#fff;padding:8px 14px;border-radius:var(--radius-sm);font-size:13px;font-weight:600;cursor:pointer;font-family:inherit;transition:all 0.15s ease}
.cp-send:hover{opacity:0.9}
.slide-up-enter-active,.slide-up-leave-active{transition:transform 0.3s cubic-bezier(0.4,0,0.2,1)}
.slide-up-enter-from,.slide-up-leave-to{transform:translateY(100%)}

/* ============ MESSAGE FORM ============ */
.msg-form{background:var(--bg-card);border-radius:var(--radius-lg);padding:18px;margin:0 16px 16px;border:1px solid var(--border-light)}
.form-row{display:flex;gap:8px;margin-bottom:10px}
.form-input{flex:1;padding:10px 12px;border:1px solid var(--border);border-radius:var(--radius-sm);font-size:14px;font-family:inherit;background:var(--bg);color:var(--text);outline:none;transition:all 0.15s ease}
.form-input:focus{border-color:var(--text)}
.mood-selector{display:flex;gap:4px}
.mood-btn{width:36px;height:36px;border:1px solid var(--border);background:var(--bg);border-radius:10px;font-size:16px;cursor:pointer;transition:all 0.15s ease;display:flex;align-items:center;justify-content:center}
.mood-btn:hover{background:var(--border-light)}
.mood-btn.active{border-color:var(--accent);background:var(--accent-light)}
.form-textarea{width:100%;padding:10px 12px;border:1px solid var(--border);border-radius:var(--radius-sm);font-size:14px;font-family:inherit;background:var(--bg);color:var(--text);outline:none;resize:none;margin-bottom:10px;line-height:1.5;transition:all 0.15s ease}
.form-textarea:focus{border-color:var(--text)}
.form-textarea::placeholder{color:var(--text-light)}
.submit-btn{width:80px;padding:9px 0;border:none;border-radius:var(--radius-sm);background:var(--accent);color:#fff;font-size:13px;cursor:pointer;font-family:inherit;transition:all 0.15s ease;flex-shrink:0;font-weight:600}
.submit-btn:hover:not(:disabled){opacity:0.9}
.submit-btn:disabled{opacity:0.3;cursor:not-allowed}
.btn-primary{background:var(--accent);color:#fff;border:none;border-radius:var(--radius);padding:10px 24px;font-size:14px;font-weight:600;cursor:pointer;transition:all 0.15s}
.btn-primary:hover:not(:disabled){opacity:0.9}
.btn-primary:disabled{opacity:0.3;cursor:not-allowed}
.btn-secondary{background:var(--bg-card);color:var(--text);border:1px solid var(--border);border-radius:var(--radius);padding:10px 24px;font-size:14px;font-weight:500;cursor:pointer;transition:all 0.15s}
.btn-secondary:hover{background:var(--bg)}

/* Message list */
.msg-list{padding:0 16px}
.msg-card{display:flex;gap:12px;margin-bottom:8px;padding:14px 0;border-bottom:1px solid var(--border-light)}
.msg-card:hover{background:none}
.msg-card.msg-private{border-color:var(--border-light);background:transparent}
.msg-avatar{width:36px;height:36px;border-radius:50%;background:#f0f0f0;color:var(--text-light);display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:600;flex-shrink:0;background-size:cover;background-position:center}
.msg-avatar.no-avatar-text span{display:none}
.msg-body{flex:1;min-width:0}
.msg-meta{display:flex;align-items:center;gap:6px;margin-bottom:3px;flex-wrap:wrap}
.msg-name{font-size:13px;font-weight:600}
.msg-private-badge{font-size:11px;flex-shrink:0}
.msg-time{font-size:11px;color:var(--text-light)}
.msg-actions-menu{display:flex;gap:2px;margin-left:auto}
.msg-action-btn{border:none;background:transparent;font-size:13px;cursor:pointer;padding:3px;opacity:0.4;transition:all 0.15s ease;border-radius:6px}
.msg-action-btn:hover{opacity:1;background:var(--bg)}
.msg-edit-wrap{margin:6px 0}
.msg-edit-actions{display:flex;gap:8px;justify-content:flex-end}
.msg-text{font-size:14px;line-height:1.5;word-break:break-word;color:var(--text)}
.msg-like-btn{margin-top:6px;border:none;background:transparent;font-size:13px;cursor:pointer;color:var(--text-light);padding:3px 6px;font-family:inherit;transition:all 0.15s ease;border-radius:6px}
.msg-like-btn:hover{color:var(--text)}

/* Private toggle */
.form-row-bottom{display:flex;align-items:center;justify-content:space-between;margin-top:8px}
.private-toggle{display:inline-flex;align-items:center;gap:6px;cursor:pointer;user-select:none;white-space:nowrap;flex-shrink:0}
.private-toggle input{display:none}
.private-label{font-size:12px;color:var(--text-light);transition:all 0.15s ease;white-space:nowrap;padding:5px 10px;background:var(--bg);border-radius:6px;border:1px solid var(--border)}
.private-toggle input:checked + .private-label{color:var(--accent);border-color:var(--accent);background:var(--accent-light);font-weight:500}

/* ============ EASTER EGG ============ */
.egg-page{position:fixed;inset:0;z-index:9997;background:linear-gradient(135deg,#0a0a0a,#1a1a1a,#0d0d0d);display:flex;align-items:center;justify-content:center;color:#fff;overflow:hidden}
.egg-content{text-align:center;z-index:2;padding:40px;max-width:400px}
.egg-heart{font-size:56px;margin-bottom:16px;animation:eggBounce 1.2s ease infinite}
@keyframes eggBounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}
.egg-title{font-size:24px;font-weight:300;margin-bottom:14px;letter-spacing:2px}
.egg-text{font-size:13px;line-height:1.9;opacity:0.8;margin-bottom:16px}
.egg-counter{font-size:11px;opacity:0.4;margin-bottom:10px}
.egg-secret{padding:10px 18px;background:rgba(255,255,255,0.06);border-radius:12px;font-size:12px;margin-bottom:14px;animation:eggGlow 1s ease infinite alternate}
@keyframes eggGlow{from{box-shadow:0 0 8px rgba(0,149,246,0.2)}to{box-shadow:0 0 24px rgba(0,149,246,0.4)}}
.egg-close{padding:10px 28px;border:1px solid rgba(255,255,255,0.2);background:transparent;color:#fff;border-radius:8px;font-size:13px;cursor:pointer;font-family:inherit;transition:var(--transition)}
.egg-close:hover{background:rgba(255,255,255,0.08)}
.egg-float-hearts{position:fixed;inset:0;pointer-events:none;overflow:hidden}
.egg-fh{position:absolute;bottom:-30px;animation:float-up 6s linear infinite;color:var(--accent);opacity:0.2}
.egg-fade-enter-active{animation:eggFadeIn 0.3s ease}
.egg-fade-leave-active{animation:eggFadeIn 0.3s ease reverse}
@keyframes eggFadeIn{from{opacity:0}to{opacity:1}}

/* ============ STORY VIEWER ============ */
.story-viewer{position:fixed;inset:0;z-index:9996;background:rgba(0,0,0,0.92);display:flex;flex-direction:column;color:#fff;cursor:pointer}
.sv-bar{padding:8px 12px}
.sv-progress{width:100%;height:2px;background:rgba(255,255,255,0.3);border-radius:1px;overflow:hidden}
.sv-progress::after{content:'';display:block;width:100%;height:100%;background:#fff;animation:storyProgress 4s linear forwards}
@keyframes storyProgress{from{width:0}to{width:100%}}
.sv-content{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:40px}
.sv-emoji{font-size:72px;margin-bottom:20px}
.sv-text{font-size:16px;text-align:center;line-height:1.8;white-space:pre-line;opacity:0.85}
.sv-user{padding:14px;text-align:center}
.sv-name{font-size:12px;font-weight:500;text-transform:uppercase;letter-spacing:1px}
.fade-enter-active,.fade-leave-active{transition:opacity 0.2s}
.fade-enter-from,.fade-leave-to{opacity:0}

/* ============ EMPTY STATE ============ */
.empty-state{text-align:center;padding:60px 20px;color:var(--text-light)}
.empty-icon{font-size:48px;display:block;margin-bottom:12px;opacity:0.4}
.empty-state p{font-size:14px;white-space:pre-line;line-height:1.6}

/* ============ FOOTER ============ */
.footer{text-align:center;padding:24px 20px;font-size:11px;color:var(--text-light);letter-spacing:0.3px}

/* ============ TOAST ============ */
.toast{position:fixed;bottom:80px;left:50%;transform:translateX(-50%);padding:10px 24px;border-radius:8px;font-size:13px;z-index:2000;box-shadow:var(--shadow-lg);white-space:nowrap;font-weight:500;background:rgba(38,38,38,0.9);color:#fff;backdrop-filter:blur(10px)}
.toast.success{background:rgba(38,38,38,0.9);color:#fff}
.toast.error{background:#ed4956;color:#fff}
.toast-enter-active{animation:toastIn 0.3s ease}
.toast-leave-active{animation:toastOut 0.2s ease}
@keyframes toastIn{from{opacity:0;transform:translateX(-50%) translateY(10px)}to{opacity:1;transform:translateX(-50%) translateY(0)}}
@keyframes toastOut{from{opacity:1}to{opacity:0}}

/* ============ CONFIRM DIALOG ============ */
.confirm-box{background:var(--bg-card);border-radius:var(--radius-lg);padding:28px 24px 20px;width:100%;max-width:300px;box-shadow:var(--shadow-lg);text-align:center;animation:confirmPop 0.2s ease}
@keyframes confirmPop{from{opacity:0;transform:scale(0.9)}to{opacity:1;transform:scale(1)}}
.confirm-icon{font-size:40px;margin-bottom:12px}
.confirm-text{font-size:14px;color:var(--text);margin-bottom:20px;line-height:1.5}
.confirm-actions{display:flex;gap:10px}
.btn-cancel{box-shadow:none}
.btn-danger{background:#ed4956;color:#fff}
.btn-danger:hover{background:#d63050}

/* ============ RESPONSIVE ============ */
@media(max-width:480px){
  .profile-header{padding:16px 12px 12px}
  .profile-avatar{width:64px;height:64px;font-size:24px}
  .profile-stats{padding:12px 16px;margin:0 12px}
  .feature-card{margin:0 12px 16px;padding:20px}
  .section-head{padding:12px 12px 10px}
  .msg-form{margin:0 12px 12px;padding:14px}
  .msg-list{padding:0 12px}
  .stories-bar{padding:12px}
  .post-card{margin:0}
  .confirm-box{padding:24px 20px 16px}
}

/* ============ SCROLLBAR ============ */
::-webkit-scrollbar{width:0;height:0}

/* ============ SELECTION ============ */
::selection{background:var(--accent-light);color:var(--accent-deep)}
</style>
