<template>
  <div class="app" :class="{ 'egg-active': showEggPage, 'dark-mode': darkMode }" @click="showUserMenu = false">
    <!-- Floating petals -->
    <div class="petals">
      <span v-for="i in 12" :key="i" class="petal" :style="petalStyle(i)">·</span>
    </div>

    <!-- Header -->
    <header class="header">
      <div class="header-inner">
        <h1 class="logo" @click="logoClicks++; checkLogoEgg(); activeSection = 'home'">
          <svg class="logo-icon" viewBox="0 0 32 32" fill="none"><circle cx="16" cy="8" r="3" fill="currentColor"/><path d="M16 11v10" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/><path d="M11 18l5 5 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>
          <span class="logo-text">onul.</span>
        </h1>
        <div class="header-actions">
          <!-- Search input -->
          <div v-if="currentUser" class="header-search" :class="{ focused: headerSearchFocused || headerSearchVal.length }">
            <svg class="hs-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
            <input v-model="headerSearchVal" class="hs-input" :placeholder="t('searchAll')" @focus="onHeaderSearchFocus" @blur="onHeaderSearchBlur" @input="onHeaderSearchInput" />
          </div>
          <!-- Login button -->
          <button v-if="!currentUser" class="login-trigger" @click="activeSection = 'login'">
            <span class="login-icon">👤</span>
          </button>
          <!-- User menu -->
          <div v-else class="user-menu">
            <span class="login-icon logged" :class="{ 'has-avatar': currentUser.avatar }" @click.stop="showUserMenu = !showUserMenu">{{ currentUser.avatar ? '' : (currentUser.nickname?.charAt(0) || currentUser.username?.charAt(0)) }}<img v-if="currentUser.avatar" :src="UPLOAD_BASE + currentUser.avatar" class="avatar-img" /></span>
            <transition name="fade">
              <div v-show="showUserMenu" class="user-dropdown" @click.stop>
                <div class="ud-name">{{ currentUser.nickname || currentUser.username }}</div>
                <button class="ud-item" @click="showUserMenu = false">{{ t('myPrivate') }}</button>
                <button class="ud-item ud-logout" @click="logout">{{ t('logout') }}</button>
              </div>
            </transition>
          </div>
        </div>
      </div>
    </header>

    <!-- Login Page -->
    <section v-if="activeSection === 'login'" class="section">
      <div class="login-page">
        <div class="lp-logo" @click="activeSection = 'home'">
          <svg class="lp-logo-icon" viewBox="0 0 32 32" fill="none"><circle cx="16" cy="8" r="3" fill="currentColor"/><path d="M16 11v10" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/><path d="M11 18l5 5 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>
          <span class="logo-text">onul.</span>
        </div>
        <p class="lp-subtitle">{{ t('profileBio') }}</p>
        <div class="lp-form">
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
    </section>

    <!-- Search Panel -->
    <transition name="fade">
      <div v-if="showSearchPanel" class="search-overlay" @click.self="showSearchPanel = false; searchQuery = ''; searchResults = []; searchPhotoResults = []; searchMsgResults = []; viewingUser = null; userFollowStatus = { is_following: false, following_count: 0, followers_count: 0, posts_count: 0 }; headerSearchVal = ''">
        <div class="search-panel">
          <div class="search-panel-header">
            <button class="sp-close" @click="showSearchPanel = false; searchQuery = ''; searchResults = []; searchPhotoResults = []; searchMsgResults = []; viewingUser = null; userFollowStatus = { is_following: false, following_count: 0, followers_count: 0, posts_count: 0 }; headerSearchVal = ''">×</button>
            <div class="sp-input-wrap">
              <input v-model="searchQuery" type="text" :placeholder="t('searchAll')" class="sp-input" @input="onUserSearch" ref="searchInput" />
            </div>
          </div>
          <!-- Search tabs -->
          <div v-if="searchQuery.trim() && !viewingUser" class="sp-tabs">
            <button :class="['sp-tab', { active: searchTab === 'users' }]" @click="searchTab = 'users'">{{ t('users') }}<span v-if="searchResults.length" class="sp-tab-count">{{ searchResults.length }}</span></button>
            <button :class="['sp-tab', { active: searchTab === 'posts' }]" @click="searchTab = 'posts'">{{ t('gallery') }}<span v-if="searchPhotoResults.length" class="sp-tab-count">{{ searchPhotoResults.length }}</span></button>
            <button :class="['sp-tab', { active: searchTab === 'messages' }]" @click="searchTab = 'messages'">{{ t('messages') }}<span v-if="searchMsgResults.length" class="sp-tab-count">{{ searchMsgResults.length }}</span></button>
          </div>
          <!-- User results -->
          <div v-if="searchTab === 'users' && searchResults.length && !viewingUser" class="sp-results">
            <div v-for="user in searchResults" :key="user.id" class="sp-user-item" @click="viewUserProfile(user)">
              <div class="sp-user-avatar" :class="{ 'no-avatar-text': user.avatar }">
                <img v-if="user.avatar" :src="UPLOAD_BASE + user.avatar" class="avatar-img" />
                <span v-else>{{ (user.nickname || user.username).charAt(0) }}</span>
              </div>
              <div class="sp-user-info">
                <span class="sp-user-name">{{ user.nickname || user.username }}</span>
                <span class="sp-user-username">@{{ user.username }}</span>
              </div>
            </div>
          </div>
          <!-- Photo results -->
          <div v-if="searchTab === 'posts' && searchPhotoResults.length && !viewingUser" class="sp-results">
            <div v-for="photo in searchPhotoResults" :key="photo.id" class="sp-photo-item" @click="showSearchPanel = false; navigateTo('gallery'); setTimeout(() => openPhotoDetail(photo), 300)">
              <div class="sp-photo-thumb"><img :src="getPhotoUrl(photo.filename)" /></div>
              <div class="sp-photo-info">
                <p class="sp-photo-caption">{{ photo.caption || t('noPhotos').split('\n')[0] }}</p>
                <span class="sp-photo-author">{{ photo.author_name || t('anonymous') }}</span>
              </div>
            </div>
          </div>
          <!-- Message results -->
          <div v-if="searchTab === 'messages' && searchMsgResults.length && !viewingUser" class="sp-results">
            <div v-for="msg in searchMsgResults" :key="msg.id" class="sp-msg-item" @click="showSearchPanel = false; navigateTo('messages')">
              <div class="sp-msg-avatar" :class="{ 'no-avatar-text': msg.author_avatar }">
                <img v-if="msg.author_avatar" :src="UPLOAD_BASE + msg.author_avatar" class="avatar-img" />
                <span v-else>{{ (msg.nickname || '?').charAt(0) }}</span>
              </div>
              <div class="sp-msg-info">
                <span class="sp-msg-name">{{ msg.nickname || t('anonymous') }}</span>
                <p class="sp-msg-content">{{ msg.content }}</p>
              </div>
            </div>
          </div>
          <!-- Viewing user profile -->
          <div class="sp-user-profile" v-if="viewingUser">
            <div class="sp-up-header" @click="viewingUser = null">
              <span class="sp-up-back">←</span>
              <span class="sp-up-title">{{ viewingUser.nickname || viewingUser.username }}</span>
            </div>
            <div class="sp-up-info">
              <div class="sp-up-avatar" :class="{ 'no-avatar-text': viewingUser.avatar }">
                <img v-if="viewingUser.avatar" :src="UPLOAD_BASE + viewingUser.avatar" class="avatar-img" />
                <span v-else>{{ (viewingUser.nickname || viewingUser.username).charAt(0) }}</span>
              </div>
              <div class="sp-up-meta">
                <h3>{{ viewingUser.nickname || viewingUser.username }}</h3>
                <p>@{{ viewingUser.username }}</p>
              </div>
              <button v-if="currentUser && currentUser.id !== viewingUser.id" class="sp-up-follow" :class="{ following: userFollowStatus.is_following }" @click.stop="toggleFollow">
                {{ userFollowStatus.is_following ? t('following') : t('follow') }}
              </button>
            </div>
            <div class="sp-up-stats">
              <div class="sp-up-stat">
                <span class="sp-up-stat-num">{{ userFollowStatus.posts_count }}</span>
                <span class="sp-up-stat-label">{{ t('posts') }}</span>
              </div>
              <div class="sp-up-stat">
                <span class="sp-up-stat-num">{{ userFollowStatus.followers_count }}</span>
                <span class="sp-up-stat-label">{{ t('followers') }}</span>
              </div>
              <div class="sp-up-stat">
                <span class="sp-up-stat-num">{{ userFollowStatus.following_count }}</span>
                <span class="sp-up-stat-label">{{ t('following') }}</span>
              </div>
            </div>
            <div class="sp-up-photos" v-if="userPhotos.length">
              <div class="profile-grid">
                <div v-for="photo in userPhotos" :key="photo.id" class="pg-item" @click="openPhotoDetail(photo)">
                  <img :src="getPhotoUrl(photo.filename)" />
                </div>
              </div>
            </div>
            <div v-else class="sp-up-empty">{{ t('noPhotos') }}</div>
          </div>
          <!-- Empty state -->
          <div class="sp-empty" v-if="searchQuery.trim() && !searchResults.length && !searchPhotoResults.length && !searchMsgResults.length && !viewingUser && !searchLoading">
            <p>{{ t('noSearchResult') }}</p>
          </div>
        </div>
      </div>
    </transition>

    <!-- Bottom Nav -->
    <nav v-if="currentUser" class="bottom-nav">
      <button v-for="item in navItems" :key="item.id"
        :class="['bnav-btn', { active: activeSection === item.id }]"
        @click="navigateTo(item.id)">
        <span class="bnav-icon" v-html="item.svg"></span>
        <span class="bnav-label">{{ t(item.id) }}</span>
      </button>
    </nav>

    <!-- Image Viewer Carousel -->
    <transition name="fade">
      <div v-if="imageViewer.show" class="image-viewer-overlay" @click="closeImageViewer">
        <button class="iv-close" @click.stop="closeImageViewer">×</button>
        <div class="iv-counter" v-if="imageViewer.images.length > 1">{{ imageViewer.current + 1 }} / {{ imageViewer.images.length }}</div>
        <button v-if="imageViewer.current > 0" class="carousel-arrow carousel-arrow-left iv-arrow" @click.stop="imageViewer.current--">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
        </button>
        <button v-if="imageViewer.current < imageViewer.images.length - 1" class="carousel-arrow carousel-arrow-right iv-arrow" @click.stop="imageViewer.current++">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
        </button>
        <div class="iv-track"
          @click.stop
          @touchstart="viewerSwipeStart" @touchmove="viewerSwipeMove" @touchend="viewerSwipeEnd"
          :style="{ transform: `translateX(calc(-${imageViewer.current * 100}% + ${imageViewer.diffX}px))` }">
          <img v-for="(src, i) in imageViewer.images" :key="i" :src="src" class="iv-img" draggable="false" />
        </div>
        <div class="iv-dots" v-if="imageViewer.images.length > 1">
          <span v-for="(_, i) in imageViewer.images" :key="i" :class="{ active: i === imageViewer.current }" @click.stop="imageViewer.current = i"></span>
        </div>
      </div>
    </transition>

    <!-- Main -->
    <main class="main" @click.capture="onGlobalClick">

      <!-- ===== HOME / PROFILE ===== -->
      <section v-if="activeSection === 'home'" class="section">
        <!-- Profile Header -->
        <div class="profile-header">
          <div class="profile-avatar-wrap">
            <div class="profile-avatar" :class="{ 'no-avatar': !currentUser?.avatar }" @dblclick="miniEgg">
              <img v-if="currentUser?.avatar" :src="UPLOAD_BASE + currentUser.avatar" class="avatar-img" />
              <span v-else style="color:#8e8e8e;font-size:24px;font-weight:300">onul</span>
            </div>
            <div class="avatar-ring"></div>
          </div>
          <div class="profile-info">
            <h2 class="profile-name">{{ currentUser ? (currentUser.nickname || currentUser.username) : 'onul' }}</h2>
            <p class="profile-bio">{{ t('profileBio') }}</p>
          </div>
        </div>

        <!-- Stats -->
        <div class="profile-stats">
          <div class="pstat">
            <span class="pstat-num">{{ myStats.posts_count }}</span>
            <span class="pstat-label">{{ t('posts') }}</span>
          </div>
          <div class="pstat-divider"></div>
          <div class="pstat">
            <span class="pstat-num">{{ myStats.followers_count }}</span>
            <span class="pstat-label">{{ t('followers') }}</span>
          </div>
          <div class="pstat-divider"></div>
          <div class="pstat">
            <span class="pstat-num">{{ myStats.following_count }}</span>
            <span class="pstat-label">{{ t('following') }}</span>
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
            <label class="upload-btn">
              <input type="file" accept="image/*" multiple @change="onFileSelect" hidden />
              <span class="upload-icon">+</span>
            </label>
          </div>
        </div>

        <!-- Feed Tabs -->
        <div class="feed-tabs" v-if="currentUser && myStats.following_count > 0">
          <button :class="['feed-tab', { active: feedTab === 'all' }]" @click="switchFeedTab('all')">{{ t('feedAll') }}</button>
          <button :class="['feed-tab', { active: feedTab === 'following' }]" @click="switchFeedTab('following')">{{ t('feedFollowing') }}</button>
        </div>

        <!-- Pull to refresh indicator -->
        <div class="pull-refresh" :style="{ height: pullDistance + 'px', opacity: pullDistance > 0 ? 1 : 0 }">
          <span v-if="refreshing">⟳</span>
          <span v-else-if="pullDistance > 20">↓ {{ t('refreshHint') }}</span>
        </div>

        <!-- Upload Modal -->
        <div v-if="showUploadModal" class="modal-overlay" @click.self="showUploadModal = false">
          <div class="modal">
            <div class="upload-previews" v-if="uploadFiles.length">
              <div v-for="(item, idx) in uploadFiles" :key="idx" class="upload-thumb-item">
                <img :src="item.preview" />
                <button class="upload-thumb-remove" @click="removeUploadPhoto(idx)">×</button>
              </div>
              <label v-if="uploadFiles.length < 10" class="upload-thumb-add">
                <input type="file" accept="image/*" multiple @change="addMorePhotos" hidden />
                <span>+</span>
              </label>
            </div>
            <div class="upload-photo-count" v-if="uploadFiles.length">{{ t('photoCount', [uploadFiles.length]) }}</div>
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
              <button class="btn-confirm" @click="confirmUpload" :disabled="uploading || !uploadFiles.length">
                {{ uploading ? '...' : '✨' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Instagram Feed -->
        <div class="feed" v-if="photos.length">
          <div v-for="photo in photos" :key="photo.id" class="post-card" :class="{ 'post-private': photo.is_private }">
            <!-- Post Header -->
            <div class="post-header">
              <div class="post-avatar" :class="{ 'no-avatar-text': photo.author_avatar }">
                <img v-if="photo.author_avatar" :src="UPLOAD_BASE + photo.author_avatar" class="avatar-img" />
                <span v-else style="font-size:12px;color:#8e8e8e">●</span>
              </div>
              <div class="post-user-info">
                <span class="post-username">{{ photo.author_name || 'onul' }}</span>
                <span class="post-location">{{ photo.location || t('inMyHeart') }}</span>
                <span v-if="isPhotoOwner(photo)" class="msg-private-badge"><span class="icon-line icon-sm" v-html="photo.is_private ? icons.lock : icons.unlock"></span></span>
                <span v-else-if="photo.is_private" class="msg-private-badge"><span class="icon-line icon-sm" v-html="icons.lock"></span></span>
              </div>
              <!-- Owner actions -->
              <div v-if="isPhotoOwner(photo)" class="post-owner-actions">
                <button class="post-action-sm" @click="startEditPhoto(photo)" :title="t('editMsg')"><span class="icon-line" v-html="icons.edit"></span></button>
                <button class="post-action-sm" @click="togglePhotoPrivate(photo)" :title="photo.is_private ? t('setPublic') : t('setPrivate')"><span class="icon-line" v-html="photo.is_private ? icons.lock : icons.unlock"></span></button>
                <button class="post-action-sm" @click="handleDeletePhoto(photo.id)" :title="t('deleteMsg')"><span class="icon-line icon-delete" v-html="icons.trash"></span></button>
              </div>
            </div>

            <!-- Edit photo caption & image -->
            <div v-if="editingPhotoId === photo.id" class="photo-edit-wrap">
              <div class="photo-edit-img-change" style="padding:0 14px 8px">
                <button class="pe-change-btn" @click="$refs['editFileInput_'+photo.id][0].click()">
                  <span class="icon-line" v-html="icons.edit"></span> {{ t('changePhoto') }}
                </button>
                <input :ref="'editFileInput_'+photo.id" type="file" accept="image/*" style="display:none" @change="(e) => editingPhotoFile = e.target.files[0] || null" />
                <span v-if="editingPhotoFile" class="pe-file-name">{{ editingPhotoFile.name }}</span>
              </div>
              <input v-model="editingPhotoCaption" type="text" class="modal-input" :placeholder="t('writeCaption')" style="margin:0 14px 8px" />
              <div class="photo-edit-actions" style="padding:0 14px 12px;display:flex;gap:8px;justify-content:flex-end">
                <button class="btn-cancel" @click="editingPhotoId = null; editingPhotoFile = null" style="font-size:12px;padding:6px 14px">{{ t('cancel') }}</button>
                <button class="btn-confirm" @click="confirmEditPhoto(photo.id)" style="font-size:12px;padding:6px 14px">{{ t('save') }}</button>
              </div>
            </div>

            <!-- Post Image (double tap to like) -->
            <div class="post-image-wrap" @dblclick="doubleTapLike(photo, $event)" :class="{ 'multi-image': (photo.extra_images || []).length }">
              <template v-if="(photo.extra_images || []).length">
                <div class="feed-carousel-wrap"
                  @touchstart="feedSwipeStart($event, photo)" @touchmove="feedSwipeMove($event, photo)" @touchend="feedSwipeEnd(photo)">
                  <button v-if="getFeedIdx(photo) > 0" class="feed-carousel-arrow feed-carousel-arrow-left" @click.stop="feedPrev(photo)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
                  </button>
                  <button v-if="getFeedIdx(photo) < (photo.extra_images || []).length" class="feed-carousel-arrow feed-carousel-arrow-right" @click.stop="feedNext(photo)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
                  </button>
                  <div class="feed-carousel" :style="{ transform: `translateX(calc(-${getFeedIdx(photo) * 100}% + ${feedSwipe.currentId === photo.id ? feedSwipe.diffX : 0}px))` }">
                    <img :src="getPhotoUrl(photo.filename)" :alt="photo.caption" loading="lazy" draggable="false" />
                    <img v-for="(ef, i) in photo.extra_images" :key="i" :src="getPhotoUrl(ef)" loading="lazy" draggable="false" />
                  </div>
                  <div class="feed-carousel-dots">
                    <span v-for="(_, i) in [photo.filename, ...(photo.extra_images || [])]" :key="i" :class="{ active: i === getFeedIdx(photo) }"></span>
                  </div>
                </div>
              </template>
              <template v-else>
                <img :src="getPhotoUrl(photo.filename)" :alt="photo.caption" loading="lazy" />
              </template>
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
                  <svg class="heart-icon" :class="{ filled: photoLikedSet.has(photo.id) }" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>
                </button>
                <button class="action-btn" @click="openComments(photo)">
                  <svg class="comment-icon" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2v10z" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </button>
              </div>
              <button :class="['action-btn', { 'bookmark-active': bookmarkedSet.has(photo.id) }]" @click="toggleBookmark(photo)">
                  <svg class="bookmark-icon" :class="{ filled: bookmarkedSet.has(photo.id) }" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none"><path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z"/></svg>
                </button>
            </div>

            <!-- Likes -->
            <div class="post-likes" v-if="photo.likes > 0">
              {{ photo.likes }} {{ t('peopleLike') }}
            </div>

            <!-- Caption -->
            <div class="post-caption" v-if="photo.caption && editingPhotoId !== photo.id">
              <strong>{{ photo.author_name || 'onul' }}</strong> {{ photo.caption }}
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
          <p>{{ feedTab === 'following' ? t('noFollowingPhotos') : t('noPhotos') }}</p>
        </div>

        <!-- Infinite scroll sentinel -->
        <div id="scroll-sentinel" class="scroll-sentinel" v-if="activeSection === 'gallery'">
          <span v-if="photoLoading">{{ t('loadingMore') }}</span>
          <span v-else-if="!photoHasMore && photos.length">{{ t('noMorePhotos') }}</span>
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
              <div class="cp-avatar" :class="{ 'no-avatar-text': c.avatar }">
                <img v-if="c.avatar" :src="UPLOAD_BASE + c.avatar" class="avatar-img" />
                <span v-else>{{ c.nickname.charAt(0) }}</span>
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
            <div class="profile-avatar lg-avatar" @click="avatarInput?.click()">
              <img v-if="currentUser?.avatar" :src="UPLOAD_BASE + currentUser.avatar" class="avatar-img" />
              <span v-else style="color:#8e8e8e;font-size:22px;font-weight:300">onul</span>
              <div class="avatar-edit-hint">✎</div>
            </div>
            <input ref="avatarInput" type="file" accept="image/*" style="display:none" @change="handleAvatarUpload">
            <div class="avatar-ring"></div>
          </div>
          <div class="profile-info">
            <h2 class="profile-name">{{ currentUser?.nickname || currentUser?.username || 'onul' }}</h2>
            <p class="profile-bio">{{ t('profileBio') }}</p>
          </div>
        </div>

        <!-- Login Required -->
        <div v-if="!currentUser" class="profile-login-required">
          <p>{{ t('loginFirst') }}</p>
          <button class="btn-primary" @click="activeSection = 'login'">{{ t('login') }}</button>
        </div>

        <!-- My Content -->
        <div v-else>
          <!-- My Stats -->
          <div class="profile-stats">
            <div class="pstat">
              <span class="pstat-num">{{ myStats.posts_count }}</span>
              <span class="pstat-label">{{ t('posts') }}</span>
            </div>
            <div class="pstat-divider"></div>
            <div class="pstat">
              <span class="pstat-num">{{ myStats.followers_count }}</span>
              <span class="pstat-label">{{ t('followers') }}</span>
            </div>
            <div class="pstat-divider"></div>
            <div class="pstat">
              <span class="pstat-num">{{ myStats.following_count }}</span>
              <span class="pstat-label">{{ t('following') }}</span>
            </div>
          </div>
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
                <div class="msg-avatar" :class="{ 'no-avatar-text': currentUser?.avatar }">
                  <img v-if="currentUser?.avatar" :src="UPLOAD_BASE + currentUser.avatar" class="avatar-img" />
                  <span v-else>{{ msg.nickname?.charAt(0) || '?' }}</span>
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
            <div class="ppm-img-wrap"
              v-if="(profilePhotoModal.extra_images || []).length"
              @touchstart="viewerSwipeStart" @touchmove="viewerSwipeMove" @touchend="viewerSwipeEnd">
              <button v-if="imageViewer.current > 0" class="carousel-arrow carousel-arrow-left" @click.stop="imageViewer.current--">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
              </button>
              <button v-if="imageViewer.current < (profilePhotoModal.extra_images || []).length" class="carousel-arrow carousel-arrow-right" @click.stop="imageViewer.current++">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
              </button>
              <div class="ppm-carousel" :style="{ transform: `translateX(calc(-${imageViewer.current * 100}% + ${imageViewer.diffX}px))` }">
                <img :src="getPhotoUrl(profilePhotoModal.filename)" class="ppm-img" draggable="false" />
                <img v-for="(ef, i) in (profilePhotoModal.extra_images || [])" :key="i" :src="getPhotoUrl(ef)" class="ppm-img" draggable="false" />
              </div>
              <div class="ppm-dots" v-if="(profilePhotoModal.extra_images || []).length">
                <span v-for="(_, i) in [profilePhotoModal.filename, ...(profilePhotoModal.extra_images || [])]" :key="i" :class="{ active: i === imageViewer.current }" @click="imageViewer.current = i"></span>
              </div>
            </div>
            <img v-else :src="getPhotoUrl(profilePhotoModal.filename)" class="ppm-img" />
            <div class="ppm-info">
              <div class="ppm-header">
                <div class="post-avatar sm-avatar" :class="{ 'no-avatar-text': profilePhotoModal.author_avatar }">
                  <img v-if="profilePhotoModal.author_avatar" :src="getPhotoUrl(profilePhotoModal.author_avatar)" class="avatar-img" />
                  <span v-else style="font-size:12px;color:#8e8e8e">●</span>
                </div>
                <div>
                  <div class="ppm-author">{{ profilePhotoModal.author_name || 'onul' }}</div>
                  <div class="ppm-location">{{ profilePhotoModal.location || t('inMyHeart') }}</div>
                </div>
              </div>
              <p class="ppm-caption">{{ profilePhotoModal.caption }}</p>
              <div class="ppm-stats">
                <span>❤️ {{ profilePhotoModal.likes || 0 }}</span>
                <span><svg style="width:14px;height:14px;vertical-align:-2px" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2v10z" stroke-linecap="round" stroke-linejoin="round"/></svg> {{ profilePhotoModal.comments_count || 0 }}</span>
                <span>{{ profilePhotoModal.created_at }}</span>
              </div>
              <div class="ppm-actions" v-if="isPhotoOwner(profilePhotoModal)">
                <button class="ppm-btn" @click="togglePhotoPrivate(profilePhotoModal)"><span class="icon-line" v-html="profilePhotoModal.is_private ? icons.lock : icons.unlock"></span></button>
                <button class="ppm-btn ppm-delete" @click="handleDeletePhoto(profilePhotoModal.id); profilePhotoModal = null"><span class="icon-line icon-delete" v-html="icons.trash"></span></button>
              </div>
            </div>
          </div>
        </div>
      </transition>

      <!-- ===== BOOKMARKS ===== -->
      <section v-if="activeSection === 'bookmarks'" class="section">
        <div class="section-head">
          <h2 class="section-title">{{ t('bookmarks') }}</h2>
          <div class="section-head-actions">
            <span class="msg-badge">{{ t('bookmarkCount', [bookmarkCount]) }}</span>
          </div>
        </div>

        <div class="feed" v-if="bookmarkPhotos.length">
          <div v-for="photo in bookmarkPhotos" :key="photo.id" class="post-card">
            <div class="post-header">
              <div class="post-avatar" :class="{ 'no-avatar-text': photo.author_avatar }">
                <img v-if="photo.author_avatar" :src="UPLOAD_BASE + photo.author_avatar" class="avatar-img" />
                <span v-else style="font-size:12px;color:#8e8e8e">●</span>
              </div>
              <div class="post-user-info">
                <span class="post-username">{{ photo.author_name || 'onul' }}</span>
                <span class="post-location">{{ photo.location || t('inMyHeart') }}</span>
              </div>
              <button :class="['action-btn', { 'bookmark-active': true }]" @click="toggleBookmark(photo)" style="font-size:18px">
                <svg class="bookmark-icon filled" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none"><path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z"/></svg>
              </button>
            </div>
            <div class="post-image-wrap" :class="{ 'multi-image': (photo.extra_images || []).length }">
              <template v-if="(photo.extra_images || []).length">
                <div class="feed-carousel-wrap"
                  @touchstart="feedSwipeStart($event, photo)" @touchmove="feedSwipeMove($event, photo)" @touchend="feedSwipeEnd(photo)">
                  <button v-if="getFeedIdx(photo) > 0" class="feed-carousel-arrow feed-carousel-arrow-left" @click.stop="feedPrev(photo)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
                  </button>
                  <button v-if="getFeedIdx(photo) < (photo.extra_images || []).length" class="feed-carousel-arrow feed-carousel-arrow-right" @click.stop="feedNext(photo)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
                  </button>
                  <div class="feed-carousel" :style="{ transform: `translateX(calc(-${getFeedIdx(photo) * 100}% + ${feedSwipe.currentId === photo.id ? feedSwipe.diffX : 0}px))` }">
                    <img :src="getPhotoUrl(photo.filename)" :alt="photo.caption" loading="lazy" draggable="false" />
                    <img v-for="(ef, i) in photo.extra_images" :key="i" :src="getPhotoUrl(ef)" loading="lazy" draggable="false" />
                  </div>
                  <div class="feed-carousel-dots">
                    <span v-for="(_, i) in [photo.filename, ...(photo.extra_images || [])]" :key="i" :class="{ active: i === getFeedIdx(photo) }"></span>
                  </div>
                </div>
              </template>
              <template v-else>
                <img :src="getPhotoUrl(photo.filename)" :alt="photo.caption" loading="lazy" />
              </template>
            </div>
            <div class="post-actions">
              <div class="post-actions-left">
                <button :class="['action-btn', { liked: photoLikedSet.has(photo.id) }]" @click="togglePhotoLike(photo)">
                  <svg class="heart-icon" :class="{ filled: photoLikedSet.has(photo.id) }" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>
                </button>
                <button class="action-btn" @click="openComments(photo)">
                  <svg class="comment-icon" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2v10z" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </button>
              </div>
            </div>
            <div class="post-likes" v-if="photo.likes > 0">{{ photo.likes }} {{ t('peopleLike') }}</div>
            <div class="post-caption" v-if="photo.caption">
              <strong>{{ photo.author_name || 'onul' }}</strong> {{ photo.caption }}
              </div>
            <div class="post-time">{{ formatTimeAgo(photo.created_at) }}</div>
          </div>
        </div>
        <div v-else class="empty-state">
          <span class="empty-icon">🔖</span>
          <p>{{ t('noBookmarks') }}</p>
        </div>
        <div id="scroll-sentinel" class="scroll-sentinel" v-if="activeSection === 'bookmarks'">
          <span v-if="bookmarkLoading">{{ t('loadingMore') }}</span>
          <span v-else-if="!bookmarkHasMore && bookmarkPhotos.length">{{ t('noMorePhotos') }}</span>
        </div>
      </section>

      <!-- ===== MESSAGES / GUESTBOOK ===== -->
      <section v-if="activeSection === 'messages'" class="section">
        <div class="section-head">
          <h2 class="section-title">{{ t('guestbook') }}</h2>
          <div class="section-head-actions">
            <span class="msg-badge">{{ messages.length }}</span>
          </div>
        </div>

        <div class="msg-form">
          <div class="form-row">
            <input v-if="!currentUser" v-model="msgNickname" type="text" :placeholder="t('yourName')" class="form-input" />
            <div v-else class="form-input" style="background:var(--accent-light);border-color:var(--accent-soft);display:flex;align-items:center;padding-left:12px;gap:6px">
              <span style="font-size:14px">👤</span>
              <span style="font-size:13px;color:var(--text)">{{ currentUser.nickname || currentUser.username }}</span>
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

        <div class="msg-list" v-if="messages.length">
          <div v-for="msg in messages" :key="msg.id" class="msg-card" :class="{ 'msg-private': msg.is_private }">
            <div class="msg-avatar" :class="{ 'no-avatar-text': msg.author_avatar }">
              <img v-if="msg.author_avatar" :src="UPLOAD_BASE + msg.author_avatar" class="avatar-img" />
              <span v-else>{{ msg.nickname.charAt(0) }}</span>
            </div>
            <div class="msg-body">
              <div class="msg-meta">
                <span class="msg-name">{{ msg.nickname }}</span>
                <span v-if="isMsgOwner(msg)" class="msg-private-badge"><span class="icon-line icon-sm" v-html="msg.is_private ? icons.lock : icons.unlock"></span></span>
                <span v-else-if="msg.is_private" class="msg-private-badge"><span class="icon-line icon-sm" v-html="icons.lock"></span></span>
                <span class="msg-time">{{ formatTimeAgo(msg.created_at) }}</span>
              <div v-if="isMsgOwner(msg)" class="msg-actions-menu">
                <button class="msg-action-btn" @click="startEditMsg(msg)" :title="t('editMsg')"><span class="icon-line" v-html="icons.edit"></span></button>
                <button class="msg-action-btn" @click="toggleMsgPrivate(msg)" :title="msg.is_private ? t('setPublic') : t('setPrivate')"><span class="icon-line" v-html="msg.is_private ? icons.lock : icons.unlock"></span></button>
                <button class="msg-action-btn" @click="handleDeleteMsg(msg.id)" :title="t('deleteMsg')"><span class="icon-line icon-delete" v-html="icons.trash"></span></button>
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
                <svg class="heart-icon-sm" :class="{ filled: msgLikedSet.has(msg.id) }" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>
                {{ msg.likes || 0 }}
              </button>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <span class="empty-icon">📝</span>
          <p>{{ t('noMessages') }}</p>
        </div>
      </section>

      <!-- ===== SETTINGS ===== -->
      <section v-if="activeSection === 'settings'" class="section">
        <div class="section-head">
          <h2 class="section-title">{{ t('settings') }}</h2>
        </div>
        <div class="settings-list">
          <div class="settings-item">
            <span class="settings-label">{{ t('settingsLang') }}</span>
            <div class="lang-switcher">
              <button v-for="lang in languages" :key="lang.code"
                :class="['lang-btn', { active: currentLang === lang.code }]"
                @click="currentLang = lang.code">{{ lang.label }}</button>
            </div>
          </div>
          <div class="settings-item">
            <span class="settings-label">{{ t('darkMode') }}</span>
            <label class="toggle-switch">
              <input type="checkbox" v-model="darkMode" />
              <span class="toggle-slider"></span>
            </label>
          </div>
          <button v-if="currentUser" class="settings-logout" @click="logout">{{ t('logout') }}</button>
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
        <div class="sv-bar">
          <div class="sv-progress"></div>
        </div>
        <div class="sv-content">
          <div class="sv-emoji">{{ viewingStory.icon }}</div>
          <p class="sv-text">{{ viewingStory.content }}</p>
        </div>
        <div class="sv-user">
          <span class="sv-name">{{ viewingStory.name }}</span>
        </div>
      </div>
    </transition>

    <!-- Footer -->
    <footer class="footer">
      <p>Made with care · {{ t('footer') }}</p>
    </footer>

    <!-- Confirm Dialog -->
    <transition name="fade">
      <div v-if="confirmDialog.show" class="modal-overlay" @click.self="confirmDialog.onCancel">
        <div class="confirm-box">
          <div class="confirm-icon"><span class="icon-line icon-confirm" v-html="confirmDialog.icon || icons.warn"></span></div>
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
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import * as api from './api.js'
import { BASE_URL, UPLOAD_BASE } from './api.js'

// ============ i18n ============
const currentLang = ref('ko')
const darkMode = ref(localStorage.getItem('diary_dark') === '1')
const languages = [
  { code: 'ko', label: '한국어' },
  { code: 'zh', label: '中文' },
  { code: 'en', label: 'EN' },
  { code: 'ja', label: '日本語' },
]

const i18n = {
  ko: {
    appTitle: 'onul.', home: '홈', gallery: '갤러리', messages: '방명록',
    profileBio: '소소한 일상 기록 ✦',
    photos: '게시물', msgCount: '개 글', likes: '좋아요',
    heroLine1: '기억하고 싶은 순간들을', heroLine2: '여기에 모아두려고 해',
    ourMoments: '기록', uploadPhoto: '올리기',
    writeCaption: '문구를 적어보세요...',
    cancel: '취소', uploading: '...', post: '게시',
    noPhotos: '아직 사진이 없어요\n첫 사진을 올려보세요!',
    noComments: '아직 댓글이 없어요',
    searchUser: '사용자 검색...', noSearchResult: '검색 결과가 없어요', searchAll: '사용자, 게시물, 방명록 검색...', users: '사용자',
    follow: '팔로우', following: '팔로잉', followers: '팔로워', posts: '게시물', followDone: '팔로우 완료 ✨', unfollowDone: '팔로우 취소',
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
    profile: '프로필', settings: '설정', changeAvatar: '사진 변경', changePhoto: '이미지 변경', changeNickname: '별명 변경', phone: '전화번호', email: '이메일', changePwd: '비밀번호 변경', oldPwd: '현재 비밀번호', newPwd: '새 비밀번호', pwdChanged: '비밀번호 변경 완료 ✨', profileSaved: '저장 완료 ✨', loginFirst: '로그인 후 이용해주세요', settingsLang: '언어', darkMode: '다크 모드',
    timeJustNow: '방금', timeMin: '분', timeHour: '시간', timeDay: '일',
    story1: '어느 날 ☀️', story2: '기록 🌙', story3: '앞으로 🌸',
    story1Content: '기분 좋은 하루였어\n바람이 좋았어 🌿',
    story2Content: '소소한 순간들이\n자꾸 기억에 남아 📖',
    story3Content: '앞으로의 이야기도\n기록하고 싶어 ✨',
    bookmarks: '저장', bookmarked: '저장됨!', unbookmarked: '저장 취소', noBookmarks: '저장한 게시물이 없어요\n관심 있는 글을 저장해보세요!', feedAll: '전체', feedFollowing: '팔로잉', bookmarkCount: (n) => `저장 ${n}개`, refreshHint: '당겨서 새로고침', loadingMore: '불러오는 중...', noMorePhotos: '더 이상 게시물이 없어요', noFollowingPhotos: '팔로우하는 사용자의\n게시물이 아직 없어요', addMorePhotos: '사진 더 추가', maxPhotosReached: '최대 10장까지', photoCount: (n) => `${n}/10`,
  },
  en: {
    appTitle: 'onul.', home: 'Home', gallery: 'Feed', messages: 'Board',
    profileBio: 'little moments ✦',
    photos: 'Posts', msgCount: 'msgs', likes: 'Likes',
    heroLine1: 'Moments I want to remember', heroLine2: 'collected here',
    ourMoments: 'Archive', uploadPhoto: 'Post',
    writeCaption: 'Write a caption...',
    cancel: 'Cancel', uploading: '...', post: 'Post',
    noPhotos: 'No photos yet\nUpload the first one!',
    noComments: 'No comments yet',
    searchUser: 'Search users...', noSearchResult: 'No results found', searchAll: 'Search users, posts, messages...', users: 'Users',
    follow: 'Follow', following: 'Following', followers: 'Followers', posts: 'Posts', followDone: 'Followed ✨', unfollowDone: 'Unfollowed',
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
    profile: 'Profile', settings: 'Settings', changeAvatar: 'Change Photo', changePhoto: 'Change Image', changeNickname: 'Change Nickname', phone: 'Phone', email: 'Email', changePwd: 'Change Password', oldPwd: 'Current Password', newPwd: 'New Password', pwdChanged: 'Password changed ✨', profileSaved: 'Saved ✨', loginFirst: 'Please login first', settingsLang: 'Language', darkMode: 'Dark Mode',
    timeJustNow: 'now', timeMin: 'm', timeHour: 'h', timeDay: 'd',
    story1: 'A Day ☀️', story2: 'Memories 🌙', story3: 'Ahead 🌸',
    story1Content: 'A nice day\nthe breeze was gentle 🌿',
    story2Content: 'Little moments\nstay in my memory 📖',
    story3Content: 'The stories yet to come\nI want to document them too ✨',
    bookmarks: 'Saved', bookmarked: 'Saved!', unbookmarked: 'Removed', noBookmarks: 'No saved posts yet\nSave posts you love!', feedAll: 'All', feedFollowing: 'Following', bookmarkCount: (n) => `${n} saved`, refreshHint: 'Pull down to refresh', loadingMore: 'Loading...', noMorePhotos: 'No more posts', noFollowingPhotos: 'No posts from people\nyou follow yet', addMorePhotos: 'Add more photos', maxPhotosReached: 'Max 10 photos', photoCount: (n) => `${n}/10`,
  },
  ja: {
    appTitle: 'onul.', home: 'ホーム', gallery: 'フィード', messages: '掲示板',
    profileBio: 'ささやかな日々の記録 ✦',
    photos: '投稿', msgCount: '件', likes: 'いいね',
    heroLine1: '覚えておきたい瞬間を', heroLine2: 'ここに集めるね',
    ourMoments: '記録', uploadPhoto: '投稿',
    writeCaption: 'キャプションを書いて...',
    cancel: 'キャンセル', uploading: '...', post: '投稿',
    noPhotos: 'まだ写真がありません\n最初の写真を投稿しましょう！',
    noComments: 'まだコメントがありません',
    searchUser: 'ユーザー検索...', noSearchResult: '検索結果がありません', searchAll: 'ユーザー、投稿、掲示板を検索...', users: 'ユーザー',
    follow: 'フォロー', following: 'フォロー中', followers: 'フォロワー', posts: '投稿', followDone: 'フォローしました ✨', unfollowDone: 'フォロー解除',
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
    profile: 'プロフィール', settings: '設定', changeAvatar: '写真変更', changePhoto: '画像変更', changeNickname: 'ニックネーム変更', phone: '電話番号', email: 'メール', changePwd: 'パスワード変更', oldPwd: '現在のパスワード', newPwd: '新しいパスワード', pwdChanged: 'パスワードを変更しました ✨', profileSaved: '保存しました ✨', loginFirst: 'ログインしてください', settingsLang: '言語', darkMode: 'ダークモード',
    timeJustNow: 'たった今', timeMin: '分', timeHour: '時間', timeDay: '日',
    story1: 'ある日 ☀️', story2: '記録 🌙', story3: 'これから 🌸',
    story1Content: '気分のいい一日だった\n風が気持ちよかったよ 🌿',
    story2Content: 'ささやかな瞬間が\nずっと記憶に残ってる 📖',
    story3Content: 'これからの物語も\n記録していきたい ✨',
    bookmarks: '保存済み', bookmarked: '保存しました!', unbookmarked: '保存解除', noBookmarks: '保存した投稿がありません\n気になる投稿を保存してみましょう!', feedAll: 'すべて', feedFollowing: 'フォロー中', bookmarkCount: (n) => `${n}件保存`, refreshHint: '下に引いて更新', loadingMore: '読み込み中...', noMorePhotos: 'これ以上投稿はありません', noFollowingPhotos: 'フォローしているユーザーの\n投稿がまだありません', addMorePhotos: '写真を追加', maxPhotosReached: '最大10枚まで', photoCount: (n) => `${n}/10`,
  },
  zh: {
    appTitle: 'onul.', home: '首页', gallery: '动态', messages: '留言板',
    profileBio: '细碎日常记录 ✦',
    photos: '动态', msgCount: '条留言', likes: '获赞',
    heroLine1: '想把记住的瞬间', heroLine2: '都留在这里',
    ourMoments: '记录', uploadPhoto: '发布',
    writeCaption: '写点什么吧...',
    cancel: '取消', uploading: '...', post: '发布',
    noPhotos: '还没有照片\n发第一条动态吧！',
    noComments: '还没有评论',
    searchUser: '搜索用户...', noSearchResult: '没有找到结果', searchAll: '搜索用户、动态、留言...', users: '用户',
    follow: '关注', following: '已关注', followers: '粉丝', posts: '作品', followDone: '关注成功 ✨', unfollowDone: '已取消关注',
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
    profile: '个人主页', settings: '设置', changeAvatar: '更换头像', changePhoto: '更换图片', changeNickname: '修改昵称', phone: '手机号', email: '邮箱', changePwd: '修改密码', oldPwd: '当前密码', newPwd: '新密码', pwdChanged: '密码修改成功 ✨', profileSaved: '保存成功 ✨', loginFirst: '请先登录', settingsLang: '语言', darkMode: '深色模式',
    timeJustNow: '刚刚', timeMin: '分钟', timeHour: '小时', timeDay: '天',
    story1: '某一天 ☀️', story2: '记录 🌙', story3: '以后 🌸',
    story1Content: '心情不错的一天\n风很舒服 🌿',
    story2Content: '细碎的瞬间\n总是留在记忆里 📖',
    story3Content: '以后的故事\n也想继续记录 ✨',
    bookmarks: '收藏', bookmarked: '已收藏!', unbookmarked: '已取消', noBookmarks: '还没有收藏的动态\n收藏感兴趣的动态吧!', feedAll: '全部', feedFollowing: '关注', bookmarkCount: (n) => `收藏 ${n}条`, refreshHint: '下拉刷新', loadingMore: '加载中...', noMorePhotos: '没有更多动态了', noFollowingPhotos: '还没有关注用户的\n动态发布', addMorePhotos: '添加更多照片', maxPhotosReached: '最多10张', photoCount: (n) => `${n}/10`,
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
const myStats = reactive({ posts_count: 0, following_count: 0, followers_count: 0 })
const tapHeart = ref(null)
const photoLikedSet = reactive(new Set())
const msgLikedSet = reactive(new Set())
const userHash = ref(localStorage.getItem('love_user_hash') || 'user_' + Math.random().toString(36).slice(2, 10))

// Auth
const currentUser = ref(null)
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

// Login requirement
const pendingSection = ref(null)

// Message edit/delete/private
const editingMsgId = ref(null)
const editingMsgContent = ref('')
const msgIsPrivate = ref(false)

// Photo edit/private
const uploadIsPrivate = ref(false)
const editingPhotoId = ref(null)
const editingPhotoCaption = ref('')
const editingPhotoFile = ref(null)

// Upload
const showUploadModal = ref(false)
const uploadFiles = ref([]) // array of {file, preview}
const uploadLocation = ref('')
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

// Search
const showSearchPanel = ref(false)
const searchQuery = ref('')
const searchTab = ref('users')
const searchResults = ref([])
const searchPhotoResults = ref([])
const searchMsgResults = ref([])
const searchLoading = ref(false)
const searchInput = ref(null)
const viewingUser = ref(null)
const userPhotos = ref([])
const userFollowStatus = ref({ is_following: false, following_count: 0, followers_count: 0, posts_count: 0 })

// Header inline search
const headerSearchVal = ref('')
const headerSearchFocused = ref(false)
let headerSearchTimer = null

// Feed: pagination & tabs
const feedTab = ref('all') // 'all' or 'following'
const photoPage = ref(1)
const photoHasMore = ref(false)
const photoLoading = ref(false)

// Bookmarks
const bookmarkedSet = reactive(new Set())
const bookmarkPhotos = ref([])
const bookmarkPage = ref(1)
const bookmarkHasMore = ref(false)
const bookmarkLoading = ref(false)
const bookmarkCount = ref(0)

// Pull to refresh
const pulling = ref(false)
const pullDistance = ref(0)
const refreshing = ref(false)
let touchStartY = 0
let mainEl = null

// Image viewer carousel
const imageViewer = reactive({ show: false, images: [], current: 0, startX: 0, diffX: 0, dragging: false })

// Feed inline carousel
const feedSwipe = reactive({ currentId: null, startX: 0, diffX: 0, dragging: false, currentIndex: {} })
function getFeedIdx(photo) { return feedSwipe.currentIndex[photo.id] || 0 }
function feedPrev(photo) {
  const idx = getFeedIdx(photo)
  if (idx > 0) feedSwipe.currentIndex[photo.id] = idx - 1
}
function feedNext(photo) {
  const idx = getFeedIdx(photo)
  const total = 1 + (photo.extra_images || []).length
  if (idx < total - 1) feedSwipe.currentIndex[photo.id] = idx + 1
}
function feedSwipeStart(e, photo) {
  feedSwipe.currentId = photo.id
  feedSwipe.startX = e.touches[0].clientX
  feedSwipe.dragging = true
}
function feedSwipeMove(e, photo) {
  if (!feedSwipe.dragging || feedSwipe.currentId !== photo.id) return
  feedSwipe.diffX = e.touches[0].clientX - feedSwipe.startX
}
function feedSwipeEnd(photo) {
  feedSwipe.dragging = false
  if (feedSwipe.currentId !== photo.id) return
  const total = 1 + (photo.extra_images || []).length
  const idx = getFeedIdx(photo)
  if (Math.abs(feedSwipe.diffX) > 40) {
    if (feedSwipe.diffX < 0 && idx < total - 1) {
      feedSwipe.currentIndex[photo.id] = idx + 1
    } else if (feedSwipe.diffX > 0 && idx > 0) {
      feedSwipe.currentIndex[photo.id] = idx - 1
    }
  }
  feedSwipe.diffX = 0
  feedSwipe.currentId = null
}

function onHeaderSearchFocus() {
  headerSearchFocused.value = true
  if (headerSearchVal.value.trim()) {
    showSearchPanel.value = true
    searchQuery.value = headerSearchVal.value
    viewUserProfile(null)
    doSearch(headerSearchVal.value.trim())
  }
}
function onHeaderSearchBlur() {
  setTimeout(() => { headerSearchFocused.value = false }, 200)
}
function onHeaderSearchInput() {
  const q = headerSearchVal.value.trim()
  if (q) {
    showSearchPanel.value = true
    searchQuery.value = q
    viewingUser.value = null
    clearTimeout(headerSearchTimer)
    headerSearchTimer = setTimeout(() => doSearch(q), 300)
  }
}

// Search all types
let searchTimer = null
async function doSearch(q) {
  searchLoading.value = true
  searchPhotoResults.value = []
  searchMsgResults.value = []
  try {
    const token = api.getToken()
    const [usersRes, photosRes, msgsRes] = await Promise.all([
      api.searchUsers(q),
      api.searchPhotos(q, token),
      api.searchMessages(q, token),
    ])
    if (usersRes.data.code === 200) searchResults.value = usersRes.data.data
    if (photosRes.data.code === 200) searchPhotoResults.value = photosRes.data.data
    if (msgsRes.data.code === 200) searchMsgResults.value = msgsRes.data.data
    // Auto-switch to tab with results
    if (searchResults.value.length) searchTab.value = 'users'
    else if (searchPhotoResults.value.length) searchTab.value = 'posts'
    else if (searchMsgResults.value.length) searchTab.value = 'messages'
  } catch (e) {
    searchResults.value = []
    searchPhotoResults.value = []
    searchMsgResults.value = []
  } finally {
    searchLoading.value = false
  }
}
async function onUserSearch() {
  clearTimeout(searchTimer)
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    searchPhotoResults.value = []
    searchMsgResults.value = []
    return
  }
  headerSearchVal.value = searchQuery.value
  searchTimer = setTimeout(() => doSearch(searchQuery.value.trim()), 300)
}

async function viewUserProfile(user) {
  viewingUser.value = user
  userPhotos.value = []
  userFollowStatus.value = { is_following: false, following_count: 0, followers_count: 0, posts_count: 0 }
  const token = api.getToken()
  try {
    const [photosRes, followRes] = await Promise.all([
      api.getUserPhotos(user.id, token),
      api.getFollowStatus(user.id, token),
    ])
    if (photosRes.data.code === 200) userPhotos.value = photosRes.data.data
    if (followRes.data.code === 200) userFollowStatus.value = followRes.data.data
  } catch (e) {}
}

async function toggleFollow() {
  if (!viewingUser.value) return
  const token = api.getToken()
  if (!token) {
    showToast(t('loginFirst'), 'info')
    return
  }
  try {
    const res = await api.followUser(viewingUser.value.id, token)
    if (res.data.code === 200) {
      userFollowStatus.value.is_following = res.data.followed
      if (res.data.followed) {
        userFollowStatus.value.followers_count += 1
        myStats.following_count += 1
        showToast(t('followDone'))
      } else {
        userFollowStatus.value.followers_count -= 1
        myStats.following_count = Math.max(0, myStats.following_count - 1)
        showToast(t('unfollowDone'))
      }
    }
  } catch (e) {}
}
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
  { id: 'home', svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H4a1 1 0 01-1-1V9.5z"/><path d="M9 21V12h6v9"/></svg>` },
  { id: 'gallery', svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>` },
  { id: 'messages', svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2v10z"/></svg>` },
  { id: 'profile', svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>` },
  { id: 'bookmarks', svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z"/></svg>` },
  { id: 'settings', svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 01-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>` },
]

// Line icons
const icons = {
  edit: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>`,
  lock: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>`,
  unlock: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 019.9-1"/></svg>`,
  trash: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6"/><path d="M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>`,
  warn: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
}

// Moods
const moods = [
  { value: 'love', icon: '🌿', key: 'mood_love' },
  { value: 'happy', icon: '😊', key: 'mood_happy' },
  { value: 'miss', icon: '🥺', key: 'mood_miss' },
  { value: 'shy', icon: '🙈', key: 'mood_shy' },
  { value: 'star', icon: '⭐', key: 'mood_star' },
]


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
        authUsername.value = ''
        authPassword.value = ''
        authNickname.value = ''
        fetchData()
        fetchMyContent()
        activeSection.value = pendingSection.value || 'home'
        pendingSection.value = null
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
        authUsername.value = ''
        authPassword.value = ''
        fetchData()
        fetchMyContent()
        activeSection.value = pendingSection.value || 'home'
        pendingSection.value = null
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
  activeSection.value = 'login'
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
  // If not logged in, only allow login section
  if (!currentUser.value && section !== 'login') {
    pendingSection.value = section
    activeSection.value = 'login'
    return false
  }
  
  // If allowed, change the active section
  activeSection.value = section
  return true
}

// Admin check
const isAdmin = computed(() => currentUser.value?.username?.includes('genhwa'))

function isMsgOwner(msg) {
  return isAdmin.value || (currentUser.value && msg.user_id && msg.user_id === currentUser.value.id)
}

function isPhotoOwner(photo) {
  return isAdmin.value || (currentUser.value && photo.user_id && photo.user_id === currentUser.value.id)
}

function openPhotoDetail(photo) {
  profilePhotoModal.value = photo
  imageViewer.current = 0
}

function isCommentOwner(comment) {
  return isAdmin.value || (currentUser.value && comment.nickname === (currentUser.value.nickname || currentUser.value.username))
}

function startEditPhoto(photo) {
  editingPhotoId.value = photo.id
  editingPhotoCaption.value = photo.caption || ''
  editingPhotoFile.value = null
}

async function confirmEditPhoto(photoId) {
  const token = api.getToken()
  if (!token) return
  try {
    const fd = new FormData()
    fd.append('caption', editingPhotoCaption.value)
    fd.append('token', token)
    if (editingPhotoFile.value) fd.append('file', editingPhotoFile.value)
    const res = await api.updatePhoto(photoId, fd)
    if (res.data.code === 200) {
      showToast(t('save'))
      editingPhotoId.value = null
      editingPhotoFile.value = null
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
  return `${UPLOAD_BASE}${filename}`
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
  const files = Array.from(e.target.files)
  if (!files.length) return
  for (const file of files) {
    if (uploadFiles.value.length >= 10) break
    if (!file.type.startsWith('image/')) continue
    uploadFiles.value.push({ file, preview: URL.createObjectURL(file) })
  }
  uploadCaption.value = ''
  uploadIsPrivate.value = false
  uploadLocation.value = ''
  showUploadModal.value = true
  fetchLocation()
  e.target.value = ''
}

function addMorePhotos(e) {
  const files = Array.from(e.target.files)
  for (const file of files) {
    if (uploadFiles.value.length >= 10) break
    if (!file.type.startsWith('image/')) continue
    uploadFiles.value.push({ file, preview: URL.createObjectURL(file) })
  }
  e.target.value = ''
}

function removeUploadPhoto(idx) {
  URL.revokeObjectURL(uploadFiles.value[idx].preview)
  uploadFiles.value.splice(idx, 1)
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
  if (!uploadFiles.value.length) return
  uploading.value = true
  try {
    const fd = new FormData()
    for (const item of uploadFiles.value) {
      fd.append('files', item.file)
    }
    fd.append('caption', uploadCaption.value)
    if (uploadLocation.value) fd.append('location', uploadLocation.value)
    const token = api.getToken()
    if (token) fd.append('token', token)
    if (currentUser.value && uploadIsPrivate.value) fd.append('is_private', '1')
    const res = await api.uploadPhoto(fd)
    if (res.data.code === 200) {
      showToast(t('toastPhotoOk'))
      showUploadModal.value = false
      for (const item of uploadFiles.value) URL.revokeObjectURL(item.preview)
      uploadFiles.value = []
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
      fetchData()
      fetchMyContent()
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
async function fetchPhotos(append = false) {
  if (photoLoading.value) return
  photoLoading.value = true
  try {
    const token = api.getToken()
    const page = append ? photoPage.value : 1
    const res = await api.getPhotos(token, page, 10, feedTab.value)
    if (res.data.code === 200) {
      const newPhotos = res.data.data
      if (append) {
        photos.value = [...photos.value, ...newPhotos]
      } else {
        photos.value = newPhotos
      }
      photoHasMore.value = res.data.has_more
      if (append) photoPage.value++
      else photoPage.value = 2
      photos.value.forEach(p => {
        if (p.likes > 0) photoLikedSet.add(p.id)
        if (p.is_bookmarked) bookmarkedSet.add(p.id)
      })
    }
  } catch (e) { console.error(e) }
  photoLoading.value = false
  fetchMyContent()
}

function loadMorePhotos() {
  if (!photoHasMore.value || photoLoading.value) return
  fetchPhotos(true)
}

function switchFeedTab(tab) {
  if (feedTab.value === tab) return
  feedTab.value = tab
  photoPage.value = 1
  photos.value = []
  fetchPhotos(false)
}

// Bookmarks
async function toggleBookmark(photo) {
  const token = api.getToken()
  if (!token) {
    showToast(t('loginFirst'), 'info')
    return
  }
  try {
    const res = await api.toggleBookmark(photo.id, token)
    if (res.data.code === 200) {
      if (res.data.bookmarked) {
        bookmarkedSet.add(photo.id)
        photo.is_bookmarked = true
        bookmarkCount.value++
        showToast(t('bookmarked'))
      } else {
        bookmarkedSet.delete(photo.id)
        photo.is_bookmarked = false
        bookmarkCount.value = Math.max(0, bookmarkCount.value - 1)
        // Remove from bookmarks page immediately
        bookmarkPhotos.value = bookmarkPhotos.value.filter(p => p.id !== photo.id)
        showToast(t('unbookmarked'))
      }
    }
  } catch (e) { console.error(e) }
}

async function fetchBookmarks(append = false) {
  if (bookmarkLoading.value) return
  bookmarkLoading.value = true
  try {
    const token = api.getToken()
    const page = append ? bookmarkPage.value : 1
    const res = await api.getBookmarks(token, page, 10)
    if (res.data.code === 200) {
      const newPhotos = res.data.data
      if (append) {
        bookmarkPhotos.value = [...bookmarkPhotos.value, ...newPhotos]
      } else {
        bookmarkPhotos.value = newPhotos
      }
      bookmarkHasMore.value = res.data.has_more
      if (append) bookmarkPage.value++
      else bookmarkPage.value = 2
    }
  } catch (e) { console.error(e) }
  bookmarkLoading.value = false
}

function loadMoreBookmarks() {
  if (!bookmarkHasMore.value || bookmarkLoading.value) return
  fetchBookmarks(true)
}

async function fetchBookmarkCount() {
  const token = api.getToken()
  if (!token) { bookmarkCount.value = 0; return }
  try {
    const res = await api.getBookmarkCount(token)
    if (res.data.code === 200) bookmarkCount.value = res.data.count
  } catch (e) {}
}

// Pull to refresh
function onTouchStart(e) {
  touchStartY = e.touches[0].clientY
  if (window.scrollY === 0) {
    pulling.value = true
    pullDistance.value = 0
  }
}
function onTouchMove(e) {
  if (!pulling.value) return
  const dy = e.touches[0].clientY - touchStartY
  if (dy > 0 && window.scrollY === 0) {
    pullDistance.value = Math.min(dy * 0.5, 60)
  } else {
    pulling.value = false
    pullDistance.value = 0
  }
}
async function onTouchEnd() {
  if (!pulling.value) return
  pulling.value = false
  if (pullDistance.value >= 45) {
    refreshing.value = true
    pullDistance.value = 0
    try {
      photoPage.value = 1
      await fetchPhotos(false)
      fetchStats()
      fetchMyStats()
    } finally {
      refreshing.value = false
    }
  } else {
    pullDistance.value = 0
  }
}

// Infinite scroll observer
let scrollObserver = null
function setupInfiniteScroll() {
  if (scrollObserver) scrollObserver.disconnect()
  scrollObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        if (activeSection.value === 'gallery') loadMorePhotos()
        else if (activeSection.value === 'bookmarks') loadMoreBookmarks()
      }
    })
  }, { rootMargin: '200px' })
}

function observeSentinel() {
  nextTick(() => {
    const el = document.getElementById('scroll-sentinel')
    if (el) scrollObserver?.observe(el)
    else scrollObserver?.disconnect()
  })
}

// Watch activeSection to trigger data fetch and infinite scroll
watch(activeSection, (val) => {
  if (val === 'gallery') {
    photoPage.value = 1
    photos.value = []
    fetchPhotos(false)
    observeSentinel()
  } else if (val === 'bookmarks') {
    bookmarkPage.value = 1
    bookmarkPhotos.value = []
    fetchBookmarks(false)
    fetchBookmarkCount()
    observeSentinel()
  } else {
    scrollObserver?.disconnect()
  }
})

async function fetchMessages() {
  try {
    const token = api.getToken()
    const res = await api.getMessages(token)
    if (res.data.code === 200) messages.value = res.data.data
  } catch (e) { console.error(e) }
  fetchMyContent()
}

async function fetchMyStats() {
  if (!currentUser.value) return
  try {
    const token = api.getToken()
    const res = await api.getFollowStatus(currentUser.value.id, token)
    if (res.data.code === 200) {
      myStats.posts_count = res.data.data.posts_count
      myStats.following_count = res.data.data.following_count
      myStats.followers_count = res.data.data.followers_count
    }
  } catch (e) {}
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
  fetchMyStats()
  fetchBookmarkCount()
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

// Image viewer carousel
function openImageViewer(photo, initialIdx = 0) {
  const allImages = [photo.filename, ...(photo.extra_images || [])]
  if (!allImages.length) return
  imageViewer.images = allImages.map(f => getPhotoUrl(f))
  imageViewer.current = initialIdx
  imageViewer.show = true
}
function closeImageViewer() {
  imageViewer.show = false
}
function viewerSwipeStart(e) {
  imageViewer.startX = e.touches[0].clientX
  imageViewer.dragging = true
}
function viewerSwipeMove(e) {
  if (!imageViewer.dragging) return
  imageViewer.diffX = e.touches[0].clientX - imageViewer.startX
}
function viewerSwipeEnd() {
  imageViewer.dragging = false
  if (Math.abs(imageViewer.diffX) > 50) {
    if (imageViewer.diffX < 0 && imageViewer.current < imageViewer.images.length - 1) {
      imageViewer.current++
    } else if (imageViewer.diffX > 0 && imageViewer.current > 0) {
      imageViewer.current--
    }
  }
  imageViewer.diffX = 0
}

// ============ Lifecycle ============
watch(showSearchPanel, (v) => {
  if (v) nextTick(() => searchInput.value?.focus())
})
watch(darkMode, (v) => {
  localStorage.setItem('diary_dark', v ? '1' : '0')
})

onMounted(() => {
  localStorage.setItem('love_user_hash', userHash.value)
  mainEl = document.querySelector('.main')
  if (mainEl) {
    mainEl.addEventListener('touchstart', onTouchStart, { passive: true })
    mainEl.addEventListener('touchmove', onTouchMove, { passive: true })
    mainEl.addEventListener('touchend', onTouchEnd)
  }
  setupInfiniteScroll()
  checkAuth().then(() => { fetchData(); fetchMyContent() })
  window.addEventListener('keydown', onKeyDown)
  quoteInterval = setInterval(() => {
    currentQuote.value = (currentQuote.value + 1) % 3
  }, 5000)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeyDown)
  if (mainEl) {
    mainEl.removeEventListener('touchstart', onTouchStart)
    mainEl.removeEventListener('touchmove', onTouchMove)
    mainEl.removeEventListener('touchend', onTouchEnd)
  }
  scrollObserver?.disconnect()
  if (quoteInterval) clearInterval(quoteInterval)
})
</script>

<style>
/* ============ RESET ============ */
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#f2f2f2;--bg-card:#ffffff;--text:#2a2a2a;--text-light:#999;
  --accent:#5a5a5a;--accent-light:#f5f5f5;--accent-soft:#eaeaea;
  --accent-deep:#3a3a3a;--gradient-soft:linear-gradient(135deg, #f5f5f5 0%, #eeeeee 50%, #f0f0f0 100%);
  --gradient-accent:linear-gradient(135deg, #888, #bbb);
  --border:#e0e0e0;--border-light:#ededed;
  --shadow:0 1px 6px rgba(0,0,0,0.04);
  --shadow-md:0 2px 12px rgba(0,0,0,0.06);
  --shadow-lg:0 6px 30px rgba(0,0,0,0.08);
  --radius:12px;--radius-sm:8px;--radius-lg:16px;
  --transition:0.2s cubic-bezier(0.4,0,0.2,1);
}
html{scroll-behavior:smooth;-webkit-tap-highlight-color:transparent}
body{
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans KR',Roboto,sans-serif;
  background:var(--bg);color:var(--text);line-height:1.5;min-height:100vh;overflow-x:hidden;
  transition:background 0.35s ease, color 0.35s ease;
  -webkit-font-smoothing:antialiased;
}
.app{max-width:480px;margin:0 auto;min-height:100vh;position:relative;background:var(--bg);transition:background 0.35s ease}

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
  background:rgba(242,242,242,0.95);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border-bottom:1px solid var(--border-light);
  transition:background 0.35s ease, border-color 0.35s ease;
}
.header-inner{display:flex;align-items:center;justify-content:space-between;padding:12px 16px}
.logo{display:flex;align-items:center;gap:6px;cursor:pointer;user-select:none;transition:transform 0.2s ease}
.logo:hover{transform:scale(1.02)}
.logo-icon{width:20px;height:20px;color:var(--text)}
.logo-text{font-size:22px;font-weight:300;letter-spacing:-0.5px;color:var(--text)}
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
  background:var(--bg-card);color:var(--text);font-weight:600;font-size:12px;
  border:1px solid var(--border);
  box-shadow:var(--shadow);
}
.login-icon.logged.has-avatar{padding:0;overflow:hidden}
.avatar-img{width:100%;height:100%;object-fit:cover;display:block;border-radius:50%}
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

/* Login page */
.login-page{display:flex;flex-direction:column;align-items:center;padding:60px 24px 40px;min-height:70vh;justify-content:center}
.lp-logo{margin-bottom:8px;cursor:pointer;display:flex;align-items:center;gap:8px;justify-content:center}
.lp-logo-icon{width:28px;height:28px;color:var(--text);opacity:0.7}
.lp-subtitle{font-size:13px;color:var(--text-light);margin-bottom:36px;font-weight:300;letter-spacing:0.5px}
.lp-form{width:100%;max-width:340px}
.lp-form .modal-input{margin-bottom:12px}
.lp-form .submit-btn{width:100%}

/* Login modal (kept for upload modal etc.) */
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
.lang-btn.active{background:var(--bg-card);color:var(--text);border:1px solid var(--border);font-weight:600}

/* ============ HEADER SEARCH ============ */
.header-search{display:flex;align-items:center;gap:6px;background:var(--bg);border-radius:10px;padding:6px 10px;border:1px solid var(--border);transition:all 0.3s cubic-bezier(0.4,0,0.2,1);width:180px;box-shadow:0 0 0 2px var(--border-light)}
.hs-icon{width:18px;height:18px;flex-shrink:0;color:var(--text-light)}
.hs-input{border:none;background:transparent;outline:none;font-size:13px;color:var(--text);width:100%;line-height:1.4}
.hs-input::placeholder{color:var(--text-light);font-size:12px}

/* Line icons */
.icon-line{display:inline-flex;width:18px;height:18px;align-items:center;justify-content:center;color:var(--text)}
.icon-line svg{width:18px;height:18px}
.icon-line.icon-sm svg{width:13px;height:13px}
.icon-line.icon-delete svg{color:#ed4956}
.icon-line.icon-confirm svg{width:28px;height:28px}

/* ============ SEARCH PANEL ============ */
.search-overlay{position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,0.4);display:flex;align-items:flex-start;justify-content:center;padding-top:0}
.search-panel{width:100%;max-width:480px;background:var(--bg);height:100vh;display:flex;flex-direction:column;animation:searchSlideIn 0.3s ease}
@keyframes searchSlideIn{from{transform:translateY(-100%)}to{transform:translateY(0)}}
.search-panel-header{display:flex;align-items:center;gap:10px;padding:12px 16px;border-bottom:1px solid var(--border-light);background:var(--bg-card)}
.sp-close{border:none;background:transparent;font-size:22px;cursor:pointer;color:var(--text);padding:4px 6px;border-radius:8px;transition:all 0.15s;line-height:1}
.sp-close:hover{background:var(--bg)}
.sp-input-wrap{flex:1}
.sp-input{width:100%;padding:10px 14px;border:1px solid var(--border);border-radius:10px;font-size:14px;font-family:inherit;background:var(--bg);color:var(--text);outline:none;transition:all 0.15s}
.sp-input:focus{border-color:var(--text)}
.sp-input::placeholder{color:var(--text-light)}
.sp-tabs{display:flex;gap:0;border-bottom:1px solid var(--border-light);background:var(--bg-card)}
.sp-tab{flex:1;padding:10px 0;border:none;background:transparent;font-size:13px;font-weight:500;color:var(--text-light);cursor:pointer;transition:all 0.2s;position:relative;display:flex;align-items:center;justify-content:center;gap:4px}
.sp-tab.active{color:var(--text);font-weight:600}
.sp-tab.active::after{content:'';position:absolute;bottom:0;left:50%;transform:translateX(-50%);width:24px;height:2px;background:var(--text);border-radius:1px}
.sp-tab-count{font-size:11px;background:var(--bg);padding:1px 6px;border-radius:10px;color:var(--text-light)}
.sp-results{flex:1;overflow-y:auto;padding:8px 0}
.sp-user-item{display:flex;align-items:center;gap:12px;padding:12px 16px;cursor:pointer;transition:background 0.15s}
.sp-user-item:hover{background:var(--border-light)}
.sp-user-item:active{background:var(--accent-light)}
.sp-user-avatar{width:40px;height:40px;border-radius:50%;background:#f0f0f0;display:flex;align-items:center;justify-content:center;font-size:16px;color:var(--text-light);flex-shrink:0;background-size:cover;background-position:center}
.sp-user-avatar.no-avatar-text span{display:none}
.sp-user-info{display:flex;flex-direction:column;gap:1px}
.sp-user-name{font-size:14px;font-weight:600;color:var(--text)}
.sp-user-username{font-size:12px;color:var(--text-light)}
.sp-photo-item{display:flex;align-items:center;gap:12px;padding:10px 16px;cursor:pointer;transition:background 0.15s}
.sp-photo-item:hover{background:var(--border-light)}
.sp-photo-thumb{width:48px;height:48px;border-radius:8px;overflow:hidden;flex-shrink:0}
.sp-photo-thumb img{width:100%;height:100%;object-fit:cover}
.sp-photo-info{flex:1;min-width:0}
.sp-photo-caption{font-size:13px;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-bottom:2px}
.sp-photo-author{font-size:12px;color:var(--text-light)}
.sp-msg-item{display:flex;align-items:flex-start;gap:12px;padding:12px 16px;cursor:pointer;transition:background 0.15s}
.sp-msg-item:hover{background:var(--border-light)}
.sp-msg-avatar{width:36px;height:36px;border-radius:50%;background:#f0f0f0;display:flex;align-items:center;justify-content:center;font-size:14px;color:var(--text-light);flex-shrink:0;background-size:cover;background-position:center}
.sp-msg-avatar.no-avatar-text span{display:none}
.sp-msg-info{flex:1;min-width:0}
.sp-msg-name{font-size:13px;font-weight:600;color:var(--text)}
.sp-msg-content{font-size:13px;color:var(--text-light);margin-top:2px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.sp-empty{text-align:center;padding:60px 20px;color:var(--text-light);font-size:14px}
.sp-user-profile{flex:1;overflow-y:auto;display:flex;flex-direction:column}
.sp-up-header{display:flex;align-items:center;gap:10px;padding:14px 16px;border-bottom:1px solid var(--border-light);cursor:pointer;background:var(--bg-card)}
.sp-up-back{font-size:18px;color:var(--text);padding:4px 6px;border-radius:8px;transition:all 0.15s}
.sp-up-header:hover .sp-up-back{background:var(--bg)}
.sp-up-title{font-size:15px;font-weight:600;color:var(--text)}
.sp-up-info{display:flex;align-items:center;gap:14px;padding:20px 16px;flex-wrap:wrap}
.sp-up-avatar{width:56px;height:56px;border-radius:50%;background:#f0f0f0;display:flex;align-items:center;justify-content:center;font-size:22px;color:var(--text-light);flex-shrink:0;background-size:cover;background-position:center}
.sp-up-avatar.no-avatar-text span{display:none}
.sp-up-meta{flex:1;min-width:0}
.sp-up-meta h3{font-size:16px;font-weight:600;margin-bottom:2px}
.sp-up-meta p{font-size:13px;color:var(--text-light)}
.sp-up-follow{padding:6px 18px;border-radius:8px;font-size:13px;font-weight:500;cursor:pointer;border:1.5px solid var(--text);background:var(--bg-card);color:var(--text);transition:all 0.2s}
.sp-up-follow.following{background:var(--bg);color:var(--text-light);border-color:var(--border)}
.sp-up-follow:active{transform:scale(0.96)}
.sp-up-stats{display:flex;gap:0;padding:0 16px 16px;border-bottom:1px solid var(--border-light)}
.sp-up-stat{flex:1;text-align:center;padding:10px 0}
.sp-up-stat-num{display:block;font-size:16px;font-weight:600;color:var(--text)}
.sp-up-stat-label{font-size:12px;color:var(--text-light)}
.sp-up-photos{padding:0 2px}
.sp-up-empty{text-align:center;padding:40px 20px;color:var(--text-light);font-size:14px}

/* ============ BOTTOM NAV ============ */
.bottom-nav{
  position:fixed;bottom:0;left:50%;transform:translateX(-50%);
  width:100%;max-width:480px;z-index:10;
  background:rgba(255,255,255,0.98);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border-top:1px solid var(--border-light);
  display:flex;justify-content:space-around;padding:8px 0 env(safe-area-inset-bottom,8px);
  transition:background 0.35s ease, border-color 0.35s ease;
}
.bnav-btn{
  display:flex;flex-direction:column;align-items:center;gap:2px;
  padding:6px 16px;border:none;background:transparent;cursor:pointer;
  color:var(--text-light);transition:all 0.3s cubic-bezier(0.4,0,0.2,1);font-family:inherit;
}
.bnav-btn:hover{opacity:0.7}
.bnav-btn.active .bnav-icon svg{stroke-width:2.2}
.bnav-btn.active .bnav-label{color:var(--text);font-weight:600}
.bnav-icon{width:24px;height:24px;transition:all 0.3s cubic-bezier(0.4,0,0.2,1);display:flex;align-items:center;justify-content:center}
.bnav-icon svg{width:22px;height:22px}
.bnav-label{font-size:10px;letter-spacing:0.3px;transition:all 0.3s cubic-bezier(0.4,0,0.2,1)}

/* ============ MAIN ============ */
.main{padding:0 0 20px;position:relative;z-index:1}
.section{animation:fadeIn 0.4s ease}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}

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
  background:var(--bg-card);color:var(--text-light);border:1px solid var(--border);
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
  transition:background 0.35s ease, border-color 0.35s ease;
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
.ppm-img-wrap{position:relative;overflow:hidden;touch-action:pan-y}
.ppm-img-wrap .carousel-arrow{position:absolute;top:50%;transform:translateY(-50%);z-index:3;width:36px;height:36px;border-radius:50%;border:none;background:rgba(0,0,0,0.35);color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:background 0.2s;backdrop-filter:blur(4px)}
.ppm-img-wrap .carousel-arrow:hover{background:rgba(0,0,0,0.6)}
.ppm-img-wrap .carousel-arrow svg{width:20px;height:20px}
.ppm-img-wrap .carousel-arrow-left{left:8px}
.ppm-img-wrap .carousel-arrow-right{right:8px}
.ppm-carousel{display:flex;transition:transform 0.3s cubic-bezier(0.25,0.46,0.45,0.94)}
.ppm-img-wrap .ppm-img{min-width:100%;max-height:60vh;object-fit:contain;background:#000}
.ppm-dots{display:flex;gap:6px;justify-content:center;padding:8px 0}
.ppm-dots span{width:6px;height:6px;border-radius:50%;background:var(--border);cursor:pointer;transition:all 0.2s}
.ppm-dots span.active{background:var(--text);width:18px;border-radius:3px}
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
  transition:background 0.35s ease, border-color 0.35s ease, transform 0.25s ease, box-shadow 0.25s ease;
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
.dot.active{background:var(--accent);width:18px;border-radius:3px;opacity:0.7}

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
  background:var(--bg-card);color:var(--text-light);font-size:12px;
  padding:4px 10px;border-radius:10px;font-weight:600;
  border:1px solid var(--border);
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
  transition:background 0.35s ease, border-color 0.35s ease;
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
.pe-change-btn{display:inline-flex;align-items:center;gap:4px;padding:5px 10px;border:1px solid var(--border);border-radius:8px;background:var(--bg-card);font-size:12px;color:var(--text);cursor:pointer;transition:all 0.15s}
.pe-change-btn:hover{background:var(--bg)}
.pe-change-btn .icon-line svg{width:13px;height:13px}
.pe-file-name{font-size:11px;color:var(--text-light);margin-left:6px}

/* Post image */
.post-image-wrap{position:relative;width:100%;aspect-ratio:1;overflow:hidden;background:#fafafa}
.post-image-wrap img{width:100%;height:100%;object-fit:cover}
.feed-carousel-wrap{position:relative;width:100%;height:100%;overflow:hidden;touch-action:pan-y}
.feed-carousel{display:flex;height:100%;transition:transform 0.3s cubic-bezier(0.25,0.46,0.45,0.94)}
.feed-carousel img{min-width:100%;height:100%;object-fit:cover}
.feed-carousel-arrow{position:absolute;top:50%;transform:translateY(-50%);z-index:3;width:30px;height:30px;border-radius:50%;border:none;background:rgba(0,0,0,0.3);color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:background 0.2s;backdrop-filter:blur(4px)}
.feed-carousel-arrow:hover{background:rgba(0,0,0,0.55)}
.feed-carousel-arrow svg{width:16px;height:16px}
.feed-carousel-arrow-left{left:8px}
.feed-carousel-arrow-right{right:8px}
.feed-carousel-dots{display:flex;gap:5px;justify-content:center;position:absolute;bottom:8px;left:50%;transform:translateX(-50%);z-index:2}
.feed-carousel-dots span{width:6px;height:6px;border-radius:50%;background:rgba(255,255,255,0.4);transition:all 0.2s}
.feed-carousel-dots span.active{background:#fff;width:16px;border-radius:3px}

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
.action-btn{border:none;background:transparent;font-size:22px;cursor:pointer;padding:2px;transition:all 0.15s ease;line-height:1;display:flex;align-items:center}
.action-btn:hover{opacity:0.6}
.action-btn:active{transform:scale(0.85)}
.action-btn.liked{animation:likePop 0.3s ease}
.heart-icon{width:24px;height:24px;transition:all 0.2s ease;color:var(--text-light)}
.heart-icon.filled{fill:#ed4956;stroke:#ed4956}
.heart-icon-sm{width:16px;height:16px;transition:all 0.2s ease;color:var(--text-light);vertical-align:middle}
.heart-icon-sm.filled{fill:#ed4956;stroke:#ed4956}
.comment-icon{width:24px;height:24px;color:var(--text-light)}
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
.comment-send{border:none;background:transparent;font-size:13px;font-weight:600;color:var(--text-light);cursor:pointer;font-family:inherit;padding:4px 6px}
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
.btn-confirm{background:var(--bg-card);color:var(--text);border:1px solid var(--border)}
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
.cp-send{border:1px solid var(--border);background:var(--bg-card);color:var(--text);padding:8px 14px;border-radius:var(--radius-sm);font-size:13px;font-weight:600;cursor:pointer;font-family:inherit;transition:all 0.15s ease}
.cp-send:hover{opacity:0.9}
.slide-up-enter-active,.slide-up-leave-active{transition:transform 0.3s cubic-bezier(0.4,0,0.2,1)}
.slide-up-enter-from,.slide-up-leave-to{transform:translateY(100%)}

/* ============ MESSAGE FORM ============ */
.msg-form{background:var(--bg-card);border-radius:var(--radius-lg);padding:18px;margin:0 16px 16px;border:1px solid var(--border-light);transition:background 0.35s ease, border-color 0.35s ease}
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
.submit-btn{width:80px;padding:9px 0;border:1px solid var(--border);border-radius:var(--radius-sm);background:var(--bg-card);color:var(--text);font-size:13px;cursor:pointer;font-family:inherit;transition:all 0.15s ease;flex-shrink:0;font-weight:600}
.submit-btn:hover:not(:disabled){opacity:0.9}
.submit-btn:disabled{opacity:0.3;cursor:not-allowed}
.btn-primary{background:var(--bg-card);color:var(--text);border:1px solid var(--border);border-radius:var(--radius);padding:10px 24px;font-size:14px;font-weight:600;cursor:pointer;transition:all 0.15s}
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
.msg-like-btn{margin-top:6px;border:none;background:transparent;font-size:13px;cursor:pointer;color:var(--text-light);padding:3px 6px;font-family:inherit;transition:all 0.15s ease;border-radius:6px;display:inline-flex;align-items:center;gap:4px}
.msg-like-btn:hover{color:var(--text)}

/* Private toggle */
.form-row-bottom{display:flex;align-items:center;justify-content:space-between;margin-top:8px}
.private-toggle{display:inline-flex;align-items:center;gap:6px;cursor:pointer;user-select:none;white-space:nowrap;flex-shrink:0}
.private-toggle input{display:none}
.private-label{font-size:12px;color:var(--text-light);transition:all 0.15s ease;white-space:nowrap;padding:5px 10px;background:var(--bg);border-radius:6px;border:1px solid var(--border)}
.private-toggle input:checked + .private-label{color:var(--accent);border-color:var(--accent);background:var(--accent-light);font-weight:500}

/* ============ SETTINGS ============ */
.settings-list{max-width:480px;margin:0 auto}
.settings-item{display:flex;align-items:center;justify-content:space-between;padding:16px 20px;background:var(--bg-card);border-radius:14px;margin-bottom:10px;border:1px solid var(--border-light);transition:background 0.35s ease, border-color 0.35s ease}
.settings-label{font-size:14px;color:var(--text);font-weight:500}
.settings-logout{width:100%;padding:14px 20px;border:1px solid var(--border-light);background:var(--bg-card);border-radius:14px;color:#ed4956;font-size:14px;font-weight:500;cursor:pointer;font-family:inherit;transition:var(--transition);margin-top:4px}
.settings-logout:hover{background:#fff5f5;border-color:#fecaca}
.settings-logout:active{transform:scale(0.98)}

/* Toggle switch */
.toggle-switch{position:relative;display:inline-block;width:44px;height:24px}
.toggle-switch input{opacity:0;width:0;height:0}
.toggle-slider{position:absolute;cursor:pointer;inset:0;background:var(--border);border-radius:24px;transition:var(--transition)}
.toggle-slider:before{content:'';position:absolute;height:18px;width:18px;left:3px;bottom:3px;background:#fff;border-radius:50%;transition:var(--transition)}
.toggle-switch input:checked + .toggle-slider{background:var(--accent)}
.toggle-switch input:checked + .toggle-slider:before{transform:translateX(20px)}

/* ============ FEED TABS ============ */
.feed-tabs{display:flex;gap:0;padding:0 16px 8px;border-bottom:1px solid var(--border-light)}
.feed-tab{flex:1;padding:8px 0;border:none;background:transparent;border-bottom:2px solid transparent;font-size:13px;font-weight:500;color:var(--text-light);cursor:pointer;transition:all 0.15s;text-align:center}
.feed-tab.active{color:var(--text);font-weight:600;border-bottom-color:var(--text)}

/* ============ BOOKMARK ICON ============ */
.bookmark-icon{width:24px;height:24px;transition:all 0.2s ease;color:var(--text-light)}
.bookmark-icon.filled{fill:var(--text);stroke:var(--text)}
.bookmark-active .bookmark-icon{fill:var(--text);stroke:var(--text)}
.action-btn.bookmark-active:active{transform:scale(0.85)}

/* ============ PULL TO REFRESH ============ */
.pull-refresh{display:flex;align-items:center;justify-content:center;overflow:hidden;transition:height 0.2s ease;font-size:13px;color:var(--text-light);gap:6px}
.pull-refresh span{opacity:0.6}
@keyframes spin{to{transform:rotate(360deg)}}
.pull-refresh span:first-child{animation:spin 1s linear infinite}

/* ============ SCROLL SENTINEL ============ */
.scroll-sentinel{text-align:center;padding:16px 0;font-size:12px;color:var(--text-light);min-height:20px}

/* ============ UPLOAD MULTI-PHOTO ============ */
.upload-previews{display:flex;gap:8px;overflow-x:auto;padding:4px 0 8px;-webkit-overflow-scrolling:touch}
.upload-previews::-webkit-scrollbar{display:none}
.upload-thumb-item{position:relative;width:80px;height:80px;border-radius:10px;overflow:hidden;flex-shrink:0}
.upload-thumb-item img{width:100%;height:100%;object-fit:cover}
.upload-thumb-remove{position:absolute;top:2px;right:2px;width:22px;height:22px;border-radius:50%;border:none;background:rgba(0,0,0,0.5);color:#fff;font-size:14px;cursor:pointer;display:flex;align-items:center;justify-content:center;line-height:1}
.upload-thumb-add{width:80px;height:80px;border-radius:10px;border:2px dashed var(--border);display:flex;align-items:center;justify-content:center;flex-shrink:0;cursor:pointer;font-size:24px;color:var(--text-light);transition:all 0.15s}
.upload-thumb-add:hover{border-color:var(--text-light)}
.upload-photo-count{font-size:12px;color:var(--text-light);margin-bottom:10px}

/* ============ MULTI-IMAGE BADGE ============ */
.multi-image-badge{position:absolute;top:10px;right:10px;width:26px;height:26px;border-radius:6px;background:rgba(0,0,0,0.4);backdrop-filter:blur(4px);display:flex;align-items:center;justify-content:center}
.multi-image-badge svg{width:14px;height:14px;color:#fff}

/* ============ IMAGE VIEWER ============ */
.image-viewer-overlay{position:fixed;inset:0;z-index:99999;background:rgba(0,0,0,0.95);display:flex;flex-direction:column;align-items:center;justify-content:center}
.iv-close{position:absolute;top:12px;right:16px;width:36px;height:36px;border-radius:50%;border:none;background:rgba(255,255,255,0.15);color:#fff;font-size:22px;cursor:pointer;display:flex;align-items:center;justify-content:center;z-index:2}
.iv-counter{position:absolute;top:16px;left:50%;transform:translateX(-50%);color:rgba(255,255,255,0.7);font-size:13px;z-index:2}
.iv-track{display:flex;width:100%;height:100%;transition:transform 0.3s cubic-bezier(0.25,0.46,0.45,0.94);touch-action:pan-y}
.iv-img{min-width:100%;height:100%;object-fit:contain;user-select:none;-webkit-user-drag:none}
.iv-dots{display:flex;gap:6px;justify-content:center;position:absolute;bottom:24px;z-index:2}
.iv-dots span{width:6px;height:6px;border-radius:50%;background:rgba(255,255,255,0.3);transition:all 0.2s;cursor:pointer}
.iv-dots span.active{background:#fff;width:18px;border-radius:3px}
.iv-arrow{position:absolute;top:50%;transform:translateY(-50%);z-index:3;width:44px;height:44px;border-radius:50%;border:none;background:rgba(0,0,0,0.35);color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:background 0.2s;backdrop-filter:blur(4px)}
.iv-arrow:hover{background:rgba(0,0,0,0.6)}
.iv-arrow svg{width:24px;height:24px}
.iv-arrow-left{left:12px}
.iv-arrow-right{right:12px}

/* ============ DARK MODE ============ */
.dark-mode{
  --bg:#0a0a0a;--bg-card:#1a1a1a;--text:#e8e8e8;--text-light:#aaa;
  --accent:#ccc;--accent-light:#222;--accent-soft:#2a2a2a;
  --accent-deep:#eee;--gradient-soft:linear-gradient(135deg, #111 0%, #1a1a1a 50%, #151515 100%);
  --gradient-accent:linear-gradient(135deg, #555, #999);
  --border:#2a2a2a;--border-light:#222;
  --shadow:0 1px 6px rgba(0,0,0,0.3);
  --shadow-md:0 2px 12px rgba(0,0,0,0.4);
  --shadow-lg:0 6px 30px rgba(0,0,0,0.5);
}
.dark-mode .header{background:rgba(10,10,10,0.95)}
.dark-mode .login-icon{background:#2a2a2a}
.dark-mode .post-card{border-color:var(--border)}
.dark-mode .msg-card{border-color:var(--border)}
.dark-mode .form-input,.dark-mode .form-textarea,.dark-mode .modal-input{background:var(--bg-card);border-color:var(--border);color:var(--text)}
.dark-mode .upload-btn:hover{background:var(--bg-card)}
.dark-mode .bottom-nav{background:rgba(10,10,10,0.95)}
.dark-mode .search-panel{background:var(--bg-card);border-color:var(--border)}
.dark-mode .modal-overlay{background:rgba(0,0,0,0.7)}
.dark-mode .login-modal{background:var(--bg-card)}
.dark-mode .auth-error{background:#2a1515;border:1px solid #3a2020}
.dark-mode .upload-modal{background:var(--bg-card)}
.dark-mode .settings-logout:hover{background:#2a1515;border-color:#3a2020}
.dark-mode .ppm-wrap{background:var(--bg-card)}
.dark-mode .comments-panel{background:var(--bg-card)}
.dark-mode .login-tab{color:var(--text-light)}
.dark-mode .login-tab.active{color:var(--text);background:var(--bg-card)}
.dark-mode .section-title{color:var(--text)}
.dark-mode .msg-name{color:var(--text)}
.dark-mode .post-username{color:var(--text)}
.dark-mode .profile-name{color:var(--text)}
.dark-mode .lp-subtitle{color:var(--text-light)}
.dark-mode .post-likes{color:var(--text)}
.dark-mode .post-caption{color:var(--text)}
.dark-mode .post-caption strong{color:var(--text)}
.dark-mode .post-avatar{background:#2a2a2a}
.dark-mode .ppm-info{background:var(--bg-card)}
.dark-mode .ppm-author{color:var(--text)}
.dark-mode .ppm-caption{color:var(--text)}
.dark-mode .ppm-stats{color:var(--text-light)}
.dark-mode .ppm-btn{background:var(--bg-card);border-color:var(--border);color:var(--text)}
.dark-mode .ppm-btn:hover{background:var(--accent-light)}
.dark-mode .ppm-delete:hover{background:#2a1515;border-color:#3a2020}
.dark-mode .post-recent-comments{color:var(--text)}
.dark-mode .post-comment-item{color:var(--text)}
.dark-mode .post-comment-item strong{color:var(--text)}
.dark-mode .post-view-comments{color:var(--text-light)}
.dark-mode .comment-send{color:var(--text-light)}
.dark-mode .quick-comment{color:var(--text)}
.dark-mode .cp-body strong{color:var(--text)}
.dark-mode .cp-body p{color:var(--text)}
.dark-mode .cp-time{color:var(--text-light)}
.dark-mode .section{background:var(--bg-card);border-color:var(--border)}
.dark-mode .feature-card{background:var(--bg-card);border-color:var(--border)}
.dark-mode .settings-item{background:var(--bg-card);border-color:var(--border)}
.dark-mode .profile-header{background:var(--bg-card)}
.dark-mode .profile-stats{background:var(--bg-card);border-color:var(--border)}
.dark-mode .upload-btn{border-color:var(--border)}
.dark-mode .upload-btn:hover{background:var(--accent-light)}
.dark-mode .upload-location{color:var(--text-light)}
.dark-mode .upload-location svg{stroke:var(--text-light)}
.dark-mode .upload-preview{background:var(--bg-card)}
.dark-mode .sp-photo-author{color:var(--text-light)}
.dark-mode .sp-msg-name{color:var(--text)}
.dark-mode .sp-msg-content{color:var(--text)}
.dark-mode .empty-state{color:var(--text-light)}
.dark-mode .pstat-label{color:var(--text-light)}
.dark-mode .profile-bio{color:var(--text-light)}
.dark-mode .form-input,.dark-mode .form-textarea{color:var(--text)}
.dark-mode .story-name{color:var(--text-light)}
.dark-mode .post-time{color:var(--text-light)}
.dark-mode .upload-caption{color:var(--text)}
.dark-mode .upload-location{color:var(--text-light)}
.dark-mode .msg-text{color:var(--text)}
.dark-mode .feed-tab{color:var(--text-light)}
.dark-mode .feed-tab.active{color:var(--text);border-bottom-color:var(--text)}
.dark-mode .bookmark-icon.filled{fill:var(--text);stroke:var(--text)}
.dark-mode .bookmark-active .bookmark-icon{fill:var(--text);stroke:var(--text)}

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
  .main{padding:0 8px 20px}
  .section{border:1px solid var(--border-light);border-radius:var(--radius-lg);margin:0 0 8px;background:var(--bg-card);overflow:hidden}
  .login-page{padding:40px 24px}
  .msg-card{border-color:var(--border-light)}
  .post-card{border-color:var(--border-light)}
  .post-recent-comments{color:var(--text)}
  .post-comment-item strong{color:var(--text)}
  .post-comment-item{color:var(--text)}
  .post-view-comments{color:var(--text-light)}
  .comment-send{color:var(--text)}
  .quick-comment{color:var(--text)}
}

/* ============ SCROLLBAR ============ */
::-webkit-scrollbar{width:0;height:0}

/* ============ SELECTION ============ */
::selection{background:var(--accent-light);color:var(--accent-deep)}
</style>
