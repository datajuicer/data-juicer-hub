/**
 * Ask AI Widget - Bundled Version
 * Generated from modular source files
 */
var AskAIWidget = (function () {
  'use strict';

  /**
   * Ask AI Widget - Internationalization Module
   */

  const I18N = {
    en: {
      title: 'Data-Juicer Q&A Copilot [Beta]',
      buttonTitle: 'Ask Juicer',
      clearTitle: 'Restart conversation',
      expandTitle: 'Expand/Collapse',
      collapseTitle: 'Collapse',
      minimizeTitle: 'Minimize',
      sendTitle: 'Send message',
      inputPlaceholder: 'Type your question here...',
      welcomeMessage: '👋 Hi! I\'m Juicer. Ask me anything about Data-Juicer!<br><br><small style="color: #888;">Powered by <a href="https://github.com/datajuicer/data-juicer-agents" target="_blank" style="color: #667eea; text-decoration: none;">data-juicer-agents</a> · Results are AI-generated and for reference only.</small>',
      welcomeConnected: '👋 Hi! I\'m Juicer. <span style="color: #28a745;">🟢 Connected</span><br>Ask me anything about Data-Juicer!<br><br><small style="color: #888;">Powered by <a href="https://github.com/datajuicer/data-juicer-agents" target="_blank" style="color: #667eea; text-decoration: none;">data-juicer-agents</a> · Results are AI-generated and for reference only.</small>',
      welcomeOffline: '👋 Hi! I\'m Juicer. <span style="color: #dc3545;">🔴 Offline Mode</span><br>Please ensure the API service is running.<br><br><small style="color: #888;">Powered by <a href="https://github.com/datajuicer/data-juicer-agents" target="_blank" style="color: #667eea; text-decoration: none;">data-juicer-agents</a> · Results are AI-generated and for reference only.</small>',
      clearConfirm: 'Are you sure you want to clear the conversation history? This action cannot be undone.',
      clearFailed: 'Failed to clear conversation history. Please try again.',
      clearError: 'Error clearing conversation history. Please check your connection and try again.',
      sendError: 'Sorry, I encountered an error. Please try again later.',
      noResponse: 'I processed your request but no valid response was generated. Please try again.',
      connectionError: 'Unable to connect to AI service, please check network or contact administrator.',
      offlineResponse: 'Sorry, the Q&A Bot API is not configured or currently unavailable. Please refer to the Data-Juicer documentation for information, or contact the administrator to configure the API service.',
      usingTool: 'Using',
      toolCalls: 'Tool Calls',
      done: 'Done',
      running: 'Running',
      like: 'Like',
      dislike: 'Dislike',
      copyMarkdown: 'Copy Markdown',
      feedbackSuccess: 'Thank you for your feedback!',
      feedbackError: 'Failed to submit feedback',
      copiedSuccess: 'Copied to clipboard!',
      helpSuffix: '\n\n---\n*If you have any questions, please visit [data-juicer issues](https://github.com/datajuicer/data-juicer/issues) or [data-juicer-agents issues](https://github.com/datajuicer/data-juicer-agents/issues)*'
    },
    zh_CN: {
      title: 'Data-Juicer Q&A Copilot [Beta]',
      buttonTitle: '询问 Juicer',
      clearTitle: '重新开始对话',
      expandTitle: '展开/收起',
      collapseTitle: '收起',
      minimizeTitle: '最小化',
      sendTitle: '发送消息',
      inputPlaceholder: '在此输入您的问题...',
      welcomeMessage: '👋 你好！我是 Juicer。问我任何关于 Data-Juicer 的问题！<br><br><small style="color: #888;">技术支持：<a href="https://github.com/datajuicer/data-juicer-agents" target="_blank" style="color: #667eea; text-decoration: none;">data-juicer-agents</a> · 结果由 AI 生成，仅供参考。</small>',
      welcomeConnected: '👋 你好！我是 Juicer。<span style="color: #28a745;">🟢 已连接</span><br>问我任何关于 Data-Juicer 的问题！<br><br><small style="color: #888;">技术支持：<a href="https://github.com/datajuicer/data-juicer-agents" target="_blank" style="color: #667eea; text-decoration: none;">data-juicer-agents</a> · 结果由 AI 生成，仅供参考。</small>',
      welcomeOffline: '👋 你好！我是 Juicer。<span style="color: #dc3545;">🔴 离线模式</span><br>请确保 API 服务正在运行。<br><br><small style="color: #888;">技术支持：<a href="https://github.com/datajuicer/data-juicer-agents" target="_blank" style="color: #667eea; text-decoration: none;">data-juicer-agents</a> · 结果由 AI 生成，仅供参考。</small>',
      clearConfirm: '确定要清除对话历史吗？此操作无法撤销。',
      clearFailed: '清除对话历史失败。请重试。',
      clearError: '清除对话历史时出错。请检查您的连接并重试。',
      sendError: '抱歉，遇到了一个错误。请稍后再试。',
      noResponse: '我处理了您的请求，但没有生成有效的响应。请重试。',
      connectionError: '无法连接到 AI 服务，请检查网络或联系管理员。',
      offlineResponse: '抱歉，Juicer API 未配置或当前不可用。请参阅 Data-Juicer 文档获取信息，或联系管理员配置 API 服务。',
      usingTool: '正在调用',
      toolCalls: '工具调用',
      done: '完成',
      running: '执行中',
      like: '点赞',
      dislike: '点踩',
      copyMarkdown: '复制 Markdown',
      feedbackSuccess: '感谢您的反馈！',
      feedbackError: '提交反馈失败',
      copiedSuccess: '已复制到剪贴板！',
      helpSuffix: '\n\n---\n*如果您有任何问题，请访问 [data-juicer issues](https://github.com/datajuicer/data-juicer/issues) 或 [data-juicer-agents issues](https://github.com/datajuicer/data-juicer-agents/issues)*'
    }
  };

  /**
   * Detect the current language from HTML attributes or URL
   * @returns {string} Language code (e.g., 'en' or 'zh_CN')
   */
  function detectLanguage() {
    // Try to get language from HTML lang attribute
    const htmlLang = document.documentElement.lang;
    if (htmlLang) {
      // Handle both 'zh-CN' and 'zh_CN' formats
      const normalizedLang = htmlLang.replace('-', '_');
      if (I18N[normalizedLang]) {
        return normalizedLang;
      }
      // Try just the language code (e.g., 'zh' from 'zh-CN')
      const langCode = normalizedLang.split('_')[0];
      if (langCode === 'zh') {
        return 'zh_CN';
      }
    }
    
    // Try to get language from meta tag
    const metaLang = document.querySelector('meta[name="language"]');
    if (metaLang && metaLang.content) {
      const normalizedLang = metaLang.content.replace('-', '_');
      if (I18N[normalizedLang]) {
        return normalizedLang;
      }
    }
    
    // Try to detect from URL (e.g., /zh_CN/version/page.html)
    const urlMatch = window.location.pathname.match(/\/(zh_CN|en)\//);
    if (urlMatch && I18N[urlMatch[1]]) {
      return urlMatch[1];
    }
    
    // Default to English
    return 'en';
  }

  /**
   * Ask AI Widget - API Communication Layer
   */

  class AskAIApi {
    constructor(sessionId, i18n) {
      this.sessionId = sessionId;
      this.i18n = i18n;
      this.apiConnected = false;
    }

    getApiBaseUrl() {
      const metaApiUrl = document.querySelector('meta[name="juicer-api-url"]');
      if (metaApiUrl && metaApiUrl.content) {
        return metaApiUrl.content;
      }

      if (window.JUICER_API_URL) {
        return window.JUICER_API_URL;
      }

      return 'http://localhost:8080';
    }

    async checkApiConnection() {
      try {
        const response = await fetch(`${this.getApiBaseUrl()}/health`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          }
        });

        if (response.ok) {
          const data = await response.json();
          this.apiConnected = data.status === 'healthy';
        } else {
          this.apiConnected = false;
        }
      } catch (error) {
        console.warn('Failed to connect to API:', error);
        this.apiConnected = false;
      }
      return this.apiConnected;
    }

    /**
     * Get the latest messages from server memory
     * @param {number} limit - Number of recent messages to fetch (default: 10)
     * @returns {Promise<Array>} Array of messages with complete metadata
     */
    async getMemory(limit = 10) {
      if (!this.apiConnected) {
        console.log('API not connected, skipping memory fetch');
        return [];
      }

      try {
        const requestBody = {
          input: [
            {
              role: "user",
              content: [
                {
                  type: "text",
                  text: "",
                },
              ],
            },
          ],
          session_id: this.sessionId,
          user_id: this.sessionId,
        };

        console.log('Fetching memory for session:', this.sessionId);

        const response = await fetch(`${this.getApiBaseUrl()}/memory`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestBody)
        });

        if (response.ok) {
          const data = await response.json();
          const messages = data.messages || [];
          console.log('Memory fetched:', messages.length, 'messages');

          // Return latest messages if limit is specified
          return limit > 0 ? messages.slice(-limit) : messages;
        } else {
          console.warn('Failed to fetch memory:', response.status);
          return [];
        }
      } catch (error) {
        console.warn('Error fetching memory:', error);
        return [];
      }
    }

    /**
     * Load conversation history from server
     * @returns {Promise<Array>} Array of historical messages
     */
    async loadConversationHistory() {
      const messages = await this.getMemory(0); // Get all messages
      console.log('Loaded', messages.length, 'historical messages');
      return messages;
    }

    async clearConversation() {
      try {
        const requestBody = {
          input: [
            {
              role: "user",
              content: [
                {
                  type: "text",
                  text: "",
                },
              ],
            },
          ],
          session_id: this.sessionId,
          user_id: this.sessionId,
        };

        const response = await fetch(`${this.getApiBaseUrl()}/clear`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'x-session-id': this.sessionId
          },
          body: JSON.stringify(requestBody)
        });

        if (response.ok) {
          console.log('Conversation history cleared successfully');
          return true;
        } else {
          console.error('Failed to clear conversation history:', response.status);
          return false;
        }
      } catch (error) {
        console.error('Error clearing conversation history:', error);
        return false;
      }
    }

    /**
     * Get AI response using streaming, then sync with server memory
     * @param {string} message - User message
     * @param {Function} onContentUpdate - Callback for content updates (text)
     * @param {Function} onToolUse - Callback for tool usage (toolName, toolArgs, callId)
     * @param {Function} onComplete - Callback when complete with verified messages (userMessage, assistantMessage)
     * @param {Function} onError - Callback for errors (error)
     * @param {Function} onToolComplete - Callback when tool execution completes (callId)
     */
    async getAIResponseStream(message, onContentUpdate, onToolUse, onComplete, onError, onToolComplete) {
      let currentStreamContent = '';
      let streamMessageId = `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      let hasReceivedContent = false;
      let streamCompletedSuccessfully = false;

      try {
        const requestBody = {
          input: [
            {
              role: "user",
              content: [
                {
                  type: "text",
                  text: message.trim(),
                },
              ],
            },
          ],
          session_id: this.sessionId,
          user_id: this.sessionId,
        };

        console.log('Sending streaming request to:', `${this.getApiBaseUrl()}/process`);

        const response = await fetch(`${this.getApiBaseUrl()}/process`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'x-session-id': this.sessionId,
          },
          body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        // Process stream
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (!line.trim() || !line.startsWith('data:')) continue;

            const jsonString = line.slice(5).trim();
            if (!jsonString) continue;

            try {
              const data = JSON.parse(jsonString);

              // End of stream
              if (data.object === "response" && data.status === "completed") {
                console.log('Stream ended normally.');
                streamCompletedSuccessfully = true;
                break;
              }

              // Handle errors
              if (data.object === "response" && data.error) {
                throw new Error(data.error.message || 'An error occurred during processing.');
              }

              // Handle tool use
              if (data.object === "message" && data.type === "plugin_call") {
                if (Array.isArray(data.content)) {
                  const toolCallWithId = data.content[0]?.type === "data" ? data.content[0].data : null;
                  const toolCallWithArgs = data.content.length > 1 ? data.content[1] : data.content[0];
                  const toolCall = toolCallWithArgs?.type === "data" ? toolCallWithArgs.data : null;

                  if (toolCall && onToolUse) {
                    const toolName = toolCall.name || 'Unknown Tool';
                    let toolArgs = toolCall.arguments || {};

                    if (typeof toolArgs === 'string') {
                      try {
                        toolArgs = JSON.parse(toolArgs);
                      } catch (e) {
                        console.warn('Failed to parse tool arguments:', e);
                        toolArgs = {};
                      }
                    }

                    const callId = toolCallWithId?.call_id || null;
                    console.log('Tool call detected:', { toolName, toolArgs, callId });
                    onToolUse(toolName, toolArgs, callId);
                  }
                }
              }

              // Handle tool output
              if (data.object === "message" && data.type === "plugin_call_output") {
                if (Array.isArray(data.content)) {
                  const outputData = data.content.find(item => item.type === "data")?.data;
                  const callId = outputData?.call_id || null;
                  const output = outputData?.output;

                  if (output && callId && onToolComplete) {
                    console.log('Tool output received for call_id:', callId);
                    onToolComplete(callId);
                  }
                }
              }

              // Handle incremental text content
              if (
                data.object === "content" &&
                data.type === "text" &&
                data.delta === true &&
                data.text !== undefined
              ) {
                if (!hasReceivedContent) {
                  currentStreamContent = '';
                  hasReceivedContent = true;
                }
                currentStreamContent += data.text;
                if (onContentUpdate) {
                  onContentUpdate(currentStreamContent);
                }
              }

              // Final message delivery
              if (
                data.object === "message" &&
                data.status === "completed" &&
                data.role === "assistant" &&
                Array.isArray(data.content)
              ) {
                const fullText = data.content
                  .filter(c => c.type === "text")
                  .map(c => c.text)
                  .join('');

                if (fullText && !hasReceivedContent) {
                  currentStreamContent = fullText;
                  hasReceivedContent = true;
                  if (onContentUpdate) {
                    onContentUpdate(currentStreamContent);
                  }
                }

                if (data.id) {
                  streamMessageId = data.id;
                  console.log('Received message ID from stream:', data.id);
                }
              }
            } catch (parseError) {
              console.warn('Failed to parse SSE data:', parseError);
            }
          }
        }

        // Validate stream completion
        if (!hasReceivedContent || !currentStreamContent.trim()) {
          console.warn('Stream completed but no content received, will fetch from memory');
          currentStreamContent = this.i18n.noResponse;
        }

        // ✨ Fetch from memory to get verified messages with complete metadata
        console.log('Stream ended, fetching latest messages from memory...');
        const recentMessages = await this.getMemory(10); // Get more messages to debug

        // Find the last user message and last assistant message
        const extractText = (content) => {
          if (Array.isArray(content)) {
            return content.filter(c => c.type === 'text').map(c => c.text).join('').trim();
          }
          return (content || '').trim();
        };

        // Get the last user message and last assistant message from memory
        let lastUserMessage = null;
        let lastAssistantMessage = null;

        for (let i = recentMessages.length - 1; i >= 0; i--) {
          const msg = recentMessages[i];
          if (!lastAssistantMessage && msg.role === 'assistant') {
            lastAssistantMessage = msg;
          }
          if (!lastUserMessage && msg.role === 'user') {
            lastUserMessage = msg;
          }
          if (lastUserMessage && lastAssistantMessage) break;
        }

        const expectedContent = message.trim();
        const lastUserContent = lastUserMessage ? extractText(lastUserMessage.content) : '';

        if (lastUserMessage && lastAssistantMessage && lastUserContent === expectedContent) {
          const assistantContent = extractText(lastAssistantMessage.content);

          console.log('✓ Memory sync successful');
          console.log('  User message ID:', lastUserMessage.id);
          console.log('  Assistant message ID:', lastAssistantMessage.id);

          // Use server content if stream was incomplete or content differs
          if (assistantContent && (!streamCompletedSuccessfully)) {
            console.log('⚠ Stream content differs from server, using server version');
            currentStreamContent = assistantContent;
            if (onContentUpdate) {
              onContentUpdate(currentStreamContent);
            }
          }

          if (onComplete) {
            onComplete(lastUserMessage, lastAssistantMessage);
          }
          return;
        } else {
          console.warn('⚠ Could not verify messages from memory');
          console.log('  Expected user content:', expectedContent.substring(0, 50));
          console.log('  Found user content:', lastUserContent.substring(0, 50));
        }

        // Fallback: memory sync failed, use stream data
        console.warn('⚠ Could not verify messages from memory, using stream data');
        if (onComplete) {
          // Create message objects from stream data
          const fallbackUserMessage = {
            id: 'user_' + streamMessageId,
            role: 'user',
            content: [{ type: 'text', text: message.trim() }]
          };
          const fallbackAssistantMessage = {
            id: streamMessageId,
            role: 'assistant',
            content: [{ type: 'text', text: currentStreamContent }]
          };
          onComplete(fallbackUserMessage, fallbackAssistantMessage);
        }

      } catch (error) {
        console.error('Stream error:', error);
        if (onError) {
          onError(error);
        }
      }
    }

    getOfflineResponse(message) {
      return this.i18n.offlineResponse;
    }

    async submitFeedback(messageId, feedbackType, comment = '') {
      try {
        const requestBody = {
          session_id: this.sessionId,
          user_id: this.sessionId,
          data: {
            feedback_type: feedbackType,
            message_id: messageId,
            comment: comment
          }
        };

        console.log('Submitting feedback:', requestBody);

        const response = await fetch(`${this.getApiBaseUrl()}/feedback`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'x-session-id': this.sessionId
          },
          body: JSON.stringify(requestBody)
        });

        if (response.ok) {
          const data = await response.json();
          console.log('Feedback submitted successfully:', data);
          return data.status === 'ok';
        } else {
          console.error('Failed to submit feedback:', response.status);
          return false;
        }
      } catch (error) {
        console.error('Error submitting feedback:', error);
        return false;
      }
    }
  }

  /**
   * Ask AI Widget - UI Management Module
   */

  class AskAIUI {
    constructor(i18n) {
      this.i18n = i18n;
      this.isOpen = false;
      this.isExpanded = false;
      this.isTyping = false;
      this.messages = [];
      
      // DOM references (will be set after createWidget)
      this.button = null;
      this.modal = null;
      this.closeBtn = null;
      this.clearBtn = null;
      this.expandBtn = null;
      this.messagesContainer = null;
      this.input = null;
      this.sendBtn = null;
    }

    /**
     * Create the widget HTML structure
     */
    createWidget() {
      const widget = document.createElement('div');
      widget.className = 'ask-ai-widget';
      widget.innerHTML = `
      <!-- Ask AI Button -->
      <button class="ask-ai-button" id="askAiButton" title="${this.i18n.buttonTitle}">
        <span class="ask-ai-button-text">Ask AI</span>
      </button>

      <!-- Chat Modal -->
      <div class="ask-ai-modal" id="askAiModal">
        <!-- Header -->
        <div class="ask-ai-header">
          <h3 class="ask-ai-title">${this.i18n.title}</h3>
          <div class="ask-ai-header-buttons">
            <button class="ask-ai-clear" id="askAiClear" title="${this.i18n.clearTitle}"><i class="fa-solid fa-arrows-rotate"></i></button>
            <button class="ask-ai-expand" id="askAiExpand" title="${this.i18n.expandTitle}"><i class="fa-solid fa-expand"></i></button>
            <button class="ask-ai-close" id="askAiClose" title="${this.i18n.minimizeTitle}"><i class="fa-solid fa-minus"></i></button>
          </div>
        </div>

        <!-- Messages Area -->
        <div class="ask-ai-messages" id="askAiMessages">
          <div class="ask-ai-welcome">
            ${this.i18n.welcomeMessage}
          </div>
        </div>

        <!-- Input Area -->
        <div class="ask-ai-input-area">
          <textarea 
            class="ask-ai-input" 
            id="askAiInput" 
            placeholder="${this.i18n.inputPlaceholder}"
            rows="1"
          ></textarea>
          <button class="ask-ai-send" id="askAiSend" title="${this.i18n.sendTitle}">
            ➤
          </button>
        </div>
      </div>
    `;

      document.body.appendChild(widget);

      // Store references
      this.button = document.getElementById('askAiButton');
      this.modal = document.getElementById('askAiModal');
      this.closeBtn = document.getElementById('askAiClose');
      this.clearBtn = document.getElementById('askAiClear');
      this.expandBtn = document.getElementById('askAiExpand');
      this.messagesContainer = document.getElementById('askAiMessages');
      this.input = document.getElementById('askAiInput');
      this.sendBtn = document.getElementById('askAiSend');
    }

    /**
     * Bind event handlers
     * @param {Object} callbacks - Object containing callback functions
     */
    bindEvents(callbacks) {
      const {
        onToggle,
        onClose,
        onClear,
        onExpand,
        onSend,
        onInputChange
      } = callbacks;

      // Toggle modal
      if (onToggle) {
        this.button.addEventListener('click', onToggle);
      }

      // Close modal
      if (onClose) {
        this.closeBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          onClose();
        });
      }

      // Clear conversation
      if (onClear) {
        this.clearBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          onClear();
        });
      }

      // Expand/collapse
      if (onExpand) {
        this.expandBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          onExpand();
        });
      }

      // Send message
      if (onSend) {
        this.sendBtn.addEventListener('click', onSend);

        // Handle Enter key in input
        this.input.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            onSend();
          }
        });
      }

      // Auto-resize textarea
      this.input.addEventListener('input', () => this.autoResizeInput());
      if (onInputChange) {
        this.input.addEventListener('input', onInputChange);
      }

      // Close modal when clicking outside
      // Note: expandBtn, closeBtn, and clearBtn checks are redundant since they are children of this.modal
      document.addEventListener('click', (e) => {
        if (this.isOpen &&
          !this.modal.contains(e.target) &&
          !this.button.contains(e.target)) {
          if (onClose) onClose();
        }
      });

      // Handle escape key
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && this.isOpen) {
          if (onClose) onClose();
        }
      });
    }

    /**
     * Open the modal
     */
    openModal() {
      this.isOpen = true;
      this.modal.classList.add('show');
      this.input.focus();
      this.scrollToBottom();
    }

    /**
     * Close the modal
     */
    closeModal() {
      this.isOpen = false;
      this.modal.classList.remove('show');
    }

    /**
     * Toggle modal open/close
     */
    toggleModal() {
      if (this.isOpen) {
        this.closeModal();
      } else {
        this.openModal();
      }
    }

    /**
     * Toggle expand/collapse state
     */
    toggleExpand() {
      this.isExpanded = !this.isExpanded;

      if (this.isExpanded) {
        this.modal.classList.add('expanded');
        const icon = this.expandBtn.querySelector('i, svg');
        if (icon) {
          icon.classList.remove('fa-expand');
          icon.classList.add('fa-compress');
        }
        this.expandBtn.title = this.i18n.collapseTitle;
      } else {
        this.modal.classList.remove('expanded');
        const icon = this.expandBtn.querySelector('i, svg');
        if (icon) {
          icon.classList.remove('fa-compress');
          icon.classList.add('fa-expand');
        }
        this.expandBtn.title = this.i18n.expandTitle;
      }
    }

    /**
     * Auto-resize the input textarea
     */
    autoResizeInput() {
      this.input.style.height = 'auto';
      this.input.style.height = Math.min(this.input.scrollHeight, 100) + 'px';
    }

    /**
     * Add a message to the chat
     * @param {string} content - Message content
     * @param {string} type - Message type ('user' or 'assistant')
     * @param {string} messageId - Optional message ID
     * @returns {HTMLElement} The created message element
     */
    addMessage(content, type, messageId = null) {
      const messageDiv = document.createElement('div');
      messageDiv.className = `ask-ai-message ${type}`;

      // Generate unique message ID if not provided
      const msgId = messageId || `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      messageDiv.setAttribute('data-message-id', msgId);

      // For assistant messages, render as markdown; for user messages, keep as plain text
      if (type === 'assistant') {
        messageDiv.innerHTML = this.renderMarkdown(content);
      } else {
        messageDiv.textContent = content;
      }

      // Add to DOM first
      this.messagesContainer.appendChild(messageDiv);

      // Then add feedback buttons for assistant messages after DOM insertion
      if (type === 'assistant') {
        // Use setTimeout to ensure DOM is fully updated
        setTimeout(() => {
          this.addFeedbackButtons(messageDiv, msgId, content);
        }, 0);
      }

      this.scrollToBottom();

      // Store message
      this.messages.push({ content, type, timestamp: Date.now(), messageId: msgId });

      return messageDiv;
    }

    /**
     * Add feedback buttons to assistant message
     * @param {HTMLElement} messageDiv - Message element
     * @param {string} messageId - Message ID
     * @param {string} content - Message content for copying
     */
    addFeedbackButtons(messageDiv, messageId, content) {
      if (!messageDiv || !messageDiv.parentNode) {
        console.warn('Message div not in DOM yet, retrying...');
        // Retry after a short delay
        setTimeout(() => {
          if (messageDiv && messageDiv.parentNode) {
            this.addFeedbackButtons(messageDiv, messageId, content);
          }
        }, 10);
        return;
      }

      // Check if wrapper already exists to avoid duplicate creation
      let messageWrapper = messageDiv.parentNode;
      if (!messageWrapper || !messageWrapper.classList.contains('ask-ai-message-wrapper')) {
        // Create wrapper
        messageWrapper = document.createElement('div');
        messageWrapper.className = 'ask-ai-message-wrapper';

        // Insert wrapper and move message
        const parentContainer = messageDiv.parentNode;
        parentContainer.insertBefore(messageWrapper, messageDiv);
        messageWrapper.appendChild(messageDiv);
      }

      // Check if feedback buttons already exist to avoid duplicate addition
      let feedbackDiv = messageWrapper.querySelector('.ask-ai-feedback-actions');
      if (!feedbackDiv) {
        feedbackDiv = document.createElement('div');
        feedbackDiv.className = 'ask-ai-feedback-actions';
        feedbackDiv.innerHTML = `
        <button class="ask-ai-feedback-btn like" data-feedback="like" title="${this.i18n.like}">
          <i class="fa-regular fa-thumbs-up"></i>
        </button>
        <button class="ask-ai-feedback-btn dislike" data-feedback="dislike" title="${this.i18n.dislike}">
          <i class="fa-regular fa-thumbs-down"></i>
        </button>
        <button class="ask-ai-feedback-btn copy" title="${this.i18n.copyMarkdown}">
          <i class="fa-regular fa-copy"></i>
        </button>
      `;

        // Append to wrapper
        messageWrapper.appendChild(feedbackDiv);
      }

      // Store content for copying
      feedbackDiv.setAttribute('data-content', content);
    }


    /**
     * Update message content while preserving tool calls and feedback buttons
     * Content is organized in segments: each tool call creates a new segment
     * @param {HTMLElement} messageDiv - Message element
     * @param {string} content - New content (cumulative from stream)
     * @param {boolean} addSuffix - Whether to add helpSuffix (default: false, used during streaming)
     */
    updateMessageContent(messageDiv, content, addSuffix = false) {
      if (!messageDiv) return;

      // Remove typing indicator if present
      const typingIndicator = messageDiv.querySelector('.typing-indicator');
      if (typingIndicator) {
        typingIndicator.remove();
      }
      
      // Only append helpSuffix when explicitly requested (at the end of response)
      const contentToRender = addSuffix ? content + (this.i18n.helpSuffix || '') : content;
      
      // Get all tool containers to find the last one
      const toolContainers = messageDiv.querySelectorAll('.tool-calls-inline');
      const lastToolContainer = toolContainers.length > 0 ? toolContainers[toolContainers.length - 1] : null;
      
      if (lastToolContainer) {
        // There are tool calls - find or create content wrapper AFTER the last tool container
        let contentWrapper = lastToolContainer.nextElementSibling;
        if (!contentWrapper || !contentWrapper.classList.contains('message-content-segment')) {
          contentWrapper = document.createElement('div');
          contentWrapper.className = 'message-content-segment';
          lastToolContainer.after(contentWrapper);
        }
        
        // Calculate what content belongs to this segment
        // We need to extract only the NEW content after the last tool call
        const segmentContent = this.extractContentAfterTools(messageDiv, content);
        contentWrapper.innerHTML = this.renderMarkdown(segmentContent);
      } else {
        // No tool calls yet - find or create the first content segment
        let contentWrapper = messageDiv.querySelector('.message-content-segment');
        if (!contentWrapper) {
          contentWrapper = document.createElement('div');
          contentWrapper.className = 'message-content-segment';
          messageDiv.appendChild(contentWrapper);
        }
        contentWrapper.innerHTML = this.renderMarkdown(contentToRender);
      }
      
      // Store full content for copying
      messageDiv.setAttribute('data-full-content', content);
      
      this.scrollToBottom();
    }

    /**
     * Extract content that should appear after the last tool call
     * This handles the cumulative content from streaming
     * @param {HTMLElement} messageDiv - Message element
     * @param {string} fullContent - Full cumulative content
     * @returns {string} Content for the current segment
     */
    extractContentAfterTools(messageDiv, fullContent) {
      // Get the content length that was rendered before the last tool call
      const lastRenderedLength = parseInt(messageDiv.getAttribute('data-content-before-last-tool') || '0', 10);
      
      // Return only the new content after the last tool call
      if (lastRenderedLength > 0 && lastRenderedLength < fullContent.length) {
        return fullContent.substring(lastRenderedLength);
      }
      
      // If no previous content recorded, return full content
      return fullContent;
    }

    /**
     * Finalize message content by adding helpSuffix
     * Called when response is complete - just adds helpSuffix to the last content segment
     * The content segments are already correctly rendered during streaming
     * @param {HTMLElement} messageDiv - Message element
     * @param {string} content - Final content (may be just the last segment from server)
     */
    finalizeMessage(messageDiv, content) {
      if (!messageDiv) return;
      
      const messageId = messageDiv.getAttribute('data-message-id');
      
      // Get all tool containers
      const toolContainers = messageDiv.querySelectorAll('.tool-calls-inline');
      
      if (toolContainers.length === 0) {
        // No tool calls - simple case, just render all content with suffix
        let contentWrapper = messageDiv.querySelector('.message-content-segment');
        if (!contentWrapper) {
          contentWrapper = document.createElement('div');
          contentWrapper.className = 'message-content-segment';
          messageDiv.appendChild(contentWrapper);
        }
        contentWrapper.innerHTML = this.renderMarkdown(content + (this.i18n.helpSuffix || ''));
      } else {
        // Has tool calls - find the last content segment and just add helpSuffix
        const lastToolContainer = toolContainers[toolContainers.length - 1];
        let lastContentSegment = lastToolContainer.nextElementSibling;
        
        if (lastContentSegment && lastContentSegment.classList.contains('message-content-segment')) {
          // Get the current content from the segment (already rendered during streaming)
          // Just re-render with helpSuffix added
          lastContentSegment.textContent || '';
          // Use the stored full content to get the correct segment content
          const fullContent = messageDiv.getAttribute('data-full-content') || content;
          const contentBeforeLastTool = parseInt(messageDiv.getAttribute('data-content-before-last-tool') || '0', 10);
          const segmentContent = contentBeforeLastTool > 0 && contentBeforeLastTool < fullContent.length 
            ? fullContent.substring(contentBeforeLastTool) 
            : fullContent;
          lastContentSegment.innerHTML = this.renderMarkdown(segmentContent + (this.i18n.helpSuffix || ''));
        } else {
          // No content segment after last tool - check if there should be one
          const fullContent = messageDiv.getAttribute('data-full-content') || content;
          const contentBeforeLastTool = parseInt(messageDiv.getAttribute('data-content-before-last-tool') || '0', 10);
          const segmentContent = contentBeforeLastTool > 0 && contentBeforeLastTool < fullContent.length 
            ? fullContent.substring(contentBeforeLastTool) 
            : '';
          
          if (segmentContent.trim()) {
            lastContentSegment = document.createElement('div');
            lastContentSegment.className = 'message-content-segment';
            lastContentSegment.innerHTML = this.renderMarkdown(segmentContent + (this.i18n.helpSuffix || ''));
            lastToolContainer.after(lastContentSegment);
          }
        }
      }
      
      // Store full content for copying (use existing if available)
      const existingFullContent = messageDiv.getAttribute('data-full-content');
      if (!existingFullContent) {
        messageDiv.setAttribute('data-full-content', content);
      }
      
      // Add feedback buttons
      if (messageId) {
        const fullContent = messageDiv.getAttribute('data-full-content') || content;
        this.addFeedbackButtons(messageDiv, messageId, fullContent);
      }
      
      this.scrollToBottom();
    }

    /**
     * Show typing indicator
     * @returns {HTMLElement} The typing indicator element
     */
    showTypingIndicator() {
      this.isTyping = true;
      this.sendBtn.disabled = true;

      const typingDiv = document.createElement('div');
      typingDiv.className = 'ask-ai-message assistant typing';
      typingDiv.id = 'typingIndicator';
      typingDiv.innerHTML = `
      <div class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    `;

      this.messagesContainer.appendChild(typingDiv);
      this.scrollToBottom();

      return typingDiv;
    }

    /**
     * Hide typing indicator
     */
    hideTypingIndicator() {
      this.isTyping = false;
      this.sendBtn.disabled = false;

      const typingIndicator = document.getElementById('typingIndicator');
      if (typingIndicator) {
        typingIndicator.remove();
      }
    }

    /**
     * Add tool call info inside message bubble
     * Consecutive tool calls go into the same tool container
     * A new tool container is only created when there's text content between tool calls
     * @param {string} toolName - Name of the tool being used
     * @param {Object} toolArgs - Tool arguments
     * @param {HTMLElement} messageDiv - Message element to add tool info to
     */
    addToolCall(toolName, toolArgs, messageDiv) {
      if (!messageDiv) return;

      // Record current content length before adding tool call
      // This is used by updateMessageContent to know where to split content
      const currentFullContent = messageDiv.getAttribute('data-full-content') || '';
      messageDiv.setAttribute('data-content-before-last-tool', currentFullContent.length.toString());

      // Check if we should reuse the last tool container or create a new one
      // Reuse if: the last child is a tool container (no text content in between)
      let toolContainer = null;
      const lastChild = messageDiv.lastElementChild;
      
      if (lastChild && lastChild.classList.contains('tool-calls-inline')) {
        // Reuse existing tool container (consecutive tool calls)
        toolContainer = lastChild;
      } else {
        // Create a new tool container (first tool call or there's text content before this)
        toolContainer = document.createElement('div');
        toolContainer.className = 'tool-calls-inline';
        
        // Add collapsible header
        const header = document.createElement('div');
        header.className = 'tool-calls-inline-header';
        header.innerHTML = `
        <span class="tool-calls-inline-title">🔧 ${this.i18n.toolCalls}</span>
        <button class="tool-calls-inline-toggle">▼</button>
      `;
        toolContainer.appendChild(header);
        
        // Add content container
        const toolContentDiv = document.createElement('div');
        toolContentDiv.className = 'tool-calls-inline-content';
        toolContainer.appendChild(toolContentDiv);
        
        // Append tool container at the end of messageDiv
        messageDiv.appendChild(toolContainer);
        
        // Add toggle functionality
        const toggleBtn = header.querySelector('.tool-calls-inline-toggle');
        toggleBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          const contentDiv = toolContainer.querySelector('.tool-calls-inline-content');
          const isCollapsed = contentDiv.style.display === 'none';
          contentDiv.style.display = isCollapsed ? 'block' : 'none';
          toggleBtn.textContent = isCollapsed ? '▼' : '▶';
          toolContainer.classList.toggle('collapsed', !isCollapsed);
        });
      }
      
      // Get the content container from the tool container
      const toolContent = toolContainer.querySelector('.tool-calls-inline-content');

      // Create tool call item
      const toolId = `tool_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const toolItem = document.createElement('div');
      toolItem.className = 'tool-call-inline running';
      toolItem.setAttribute('data-tool-id', toolId);
      
      // Format arguments for display (compact)
      let argsPreview = '';
      if (toolArgs && Object.keys(toolArgs).length > 0) {
        const argsList = Object.entries(toolArgs).map(([key, value]) => {
          const displayValue = typeof value === 'string' && value.length > 50 
            ? value.substring(0, 50) + '...' 
            : JSON.stringify(value);
          return `${key}: ${this.escapeHtml(displayValue)}`;
        }).join(', ');
        argsPreview = `<div class="tool-args-preview">${argsList}</div>`;
      }

      toolItem.innerHTML = `
      <div class="tool-inline-header">
        <span class="tool-name-inline">${this.escapeHtml(toolName)}</span>
        <span class="tool-status-inline running"></span>
      </div>
      ${argsPreview}
    `;

      toolContent.appendChild(toolItem);
      this.scrollToBottom();

      return toolId;
    }

    /**
     * Mark a tool call as completed
     * @param {string} toolId - Tool ID to mark as done
     */
    markToolCallDone(toolId) {
      const toolItem = this.messagesContainer.querySelector(`[data-tool-id="${toolId}"]`);
      if (toolItem) {
        toolItem.classList.remove('running');
        const statusSpan = toolItem.querySelector('.tool-status-inline');
        if (statusSpan) {
          statusSpan.textContent = 'Done';
          statusSpan.classList.remove('running');
        }
      }
    }

    /**
     * Scroll messages container to bottom
     */
    scrollToBottom() {
      setTimeout(() => {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
      }, 100);
    }

    /**
     * Clear all messages from UI
     */
    clearMessages() {
      this.messages = [];
      const existingMessages = this.messagesContainer.querySelectorAll('.ask-ai-message, .ask-ai-message-wrapper');
      existingMessages.forEach(msg => msg.remove());
      // Note: Welcome message is intentionally kept - it will be updated by addWelcomeMessage()
    }

    /**
     * Add welcome message
     * @param {boolean} apiConnected - Whether API is connected
     */
    addWelcomeMessage(apiConnected) {
      // Always show welcome message, regardless of history
      let welcomeElement = this.messagesContainer.querySelector('.ask-ai-welcome');
      
      // If welcome element doesn't exist, create it
      if (!welcomeElement) {
        welcomeElement = document.createElement('div');
        welcomeElement.className = 'ask-ai-welcome';
        // Insert at the beginning of messages container
        this.messagesContainer.insertBefore(welcomeElement, this.messagesContainer.firstChild);
      }
      
      // Update welcome message content based on connection status
      if (apiConnected) {
        welcomeElement.innerHTML = this.i18n.welcomeConnected;
      } else {
        welcomeElement.innerHTML = this.i18n.welcomeOffline;
      }
    }

    /**
     * Render markdown text to HTML
     * @param {string} text - Markdown text
     * @returns {string} HTML string
     */
    renderMarkdown(text) {
      if (!text) return '';

      try {
        const renderer = new marked.Renderer();

        // Custom heading renderer - use CSS classes instead of inline styles
        renderer.heading = (token) => {
          const escapedText = this.escapeHtml(token.text);
          return `<h${token.depth}>${escapedText}</h${token.depth}>`;
        };

        // Custom link renderer - open in new tab
        renderer.link = (token) => {
          const href = token.href;
          const title = token.title ? ` title="${this.escapeHtml(token.title)}"` : '';
          const text = token.text;
          return `<a href="${href}"${title} target="_blank" rel="noopener noreferrer">${text}</a>`;
        };

        return marked.parse(text, { renderer });
      } catch (error) {
        console.error('Markdown rendering error:', error);
        return this.escapeHtml(text).replace(/\n/g, '<br>');
      }
    }

    /**
     * Escape HTML special characters
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }

    /**
     * Observe theme changes from the Sphinx theme
     */
    observeThemeChanges() {
      // Apply initial theme
      this.updateWidgetTheme();

      // Watch for theme changes on html or body element
      const targetNode = document.documentElement || document.body;

      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          if (mutation.type === 'attributes' &&
            (mutation.attributeName === 'class' ||
              mutation.attributeName === 'data-theme' ||
              mutation.attributeName === 'data-bs-theme')) {
            this.updateWidgetTheme();
          }
        });
      });

      observer.observe(targetNode, {
        attributes: true,
        attributeFilter: ['class', 'data-theme', 'data-bs-theme']
      });
    }

    /**
     * Update widget theme based on page theme
     */
    updateWidgetTheme() {
      const html = document.documentElement;

      // Check various theme indicators to match the observer's scope
      const isDark = html.getAttribute('data-theme') === 'dark' ||
                     html.getAttribute('data-bs-theme') === 'dark' ||
                     document.body.classList.contains('theme-dark');

      if (isDark) {
        this.modal.classList.add('theme-dark');
        this.button.classList.add('theme-dark');
      } else {
        this.modal.classList.remove('theme-dark');
        this.button.classList.remove('theme-dark');
      }
    }

    /**
     * Get current input value
     * @returns {string} Input value
     */
    getInputValue() {
      return this.input.value;
    }

    /**
     * Clear input value
     */
    clearInput() {
      this.input.value = '';
      this.autoResizeInput();
    }
  }

  /**
   * Ask AI Widget - Main Controller
   * 
   * This is the main entry point that integrates all modules:
   * - I18N: Internationalization
   * - API: Communication with backend
   * - UI: User interface management
   */


  class AskAIWidget {
    constructor() {
      // Check if marked library is loaded
      if (typeof marked === 'undefined') {
        console.error('Marked library not loaded!');
        console.info('Add this to your HTML: <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>');
        return;
      }

      // Initialize session and language
      this.sessionId = this.generateSessionId();
      this.language = detectLanguage();
      this.i18n = I18N[this.language.replace('-', '_')] || I18N.en;

      // Initialize modules
      this.api = new AskAIApi(this.sessionId, this.i18n);
      this.ui = new AskAIUI(this.i18n);

      // Configure marked
      marked.setOptions({
        breaks: true,
        gfm: true,
        headerIds: false,
        mangle: false,
      });

      this.init();
    }

    /**
     * Generate or retrieve session ID
     * @returns {string} Session ID
     */
    generateSessionId() {
      // Try to get existing session ID from sessionStorage
      let sessionId = sessionStorage.getItem('ask-ai-session-id');

      if (!sessionId) {
        // Generate new session ID if none exists
        sessionId = `browser-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        sessionStorage.setItem('ask-ai-session-id', sessionId);
      }

      console.log('Using session ID:', sessionId);
      return sessionId;
    }

    /**
     * Initialize the widget
     */
    async init() {
      // Create UI
      this.ui.createWidget();
      
      // Bind events
      this.ui.bindEvents({
        onToggle: () => this.ui.toggleModal(),
        onClose: () => this.ui.closeModal(),
        onClear: () => this.clearConversation(),
        onExpand: () => this.ui.toggleExpand(),
        onSend: () => this.sendMessage(),
      });

      // Bind feedback button events
      this.bindFeedbackEvents();

      // Observe theme changes
      this.ui.observeThemeChanges();

      // Check API connection
      await this.api.checkApiConnection();

      // Load conversation history
      await this.loadConversationHistory();

      // Add welcome message
      this.addWelcomeMessage();
    }

    /**
     * Bind feedback button events using event delegation
     */
    bindFeedbackEvents() {
      this.ui.messagesContainer.addEventListener('click', async (e) => {
        const target = e.target.closest('.ask-ai-feedback-btn');
        if (!target) return;

        const messageWrapper = target.closest('.ask-ai-message-wrapper');
        const messageDiv = messageWrapper?.querySelector('.ask-ai-message');
        const messageId = messageDiv?.getAttribute('data-message-id');
        
        if (!messageId) {
          console.warn('No message ID found for feedback');
          return;
        }

        const feedbackType = target.getAttribute('data-feedback');

        // Handle copy button
        if (target.classList.contains('copy')) {
          const feedbackDiv = target.closest('.ask-ai-feedback-actions');
          const content = feedbackDiv?.getAttribute('data-content') || '';
          await this.copyToClipboard(content);
          return;
        }

        // Handle like/dislike buttons
        if (feedbackType && messageId) {
          await this.handleFeedback(target, messageId, feedbackType);
          console.log('Submitting feedback with message ID:', messageId);
        }
      });
    }

    /**
     * Handle feedback submission
     * @param {HTMLElement} button - Feedback button element
     * @param {string} messageId - Message ID
     * @param {string} feedbackType - Feedback type ('like' or 'dislike')
     */
    async handleFeedback(button, messageId, feedbackType) {
      // Get all feedback buttons for this message
      const feedbackDiv = button.closest('.ask-ai-feedback-actions');
      const allButtons = feedbackDiv.querySelectorAll('.ask-ai-feedback-btn[data-feedback]');

      // Check if clicking the same button again (toggle off)
      if (button.classList.contains('active')) {
        button.classList.remove('active');
        return;
      }

      // Remove active state from all feedback buttons
      allButtons.forEach(btn => btn.classList.remove('active'));

      // Add active state to clicked button
      button.classList.add('active');

      // Submit feedback to backend
      const success = await this.api.submitFeedback(messageId, feedbackType);

      if (success) {
        console.log(`Feedback "${feedbackType}" submitted for message ${messageId}`);
      } else {
        console.error('Failed to submit feedback');
        // Remove active state on failure
        button.classList.remove('active');
      }
    }

    /**
     * Copy content to clipboard
     * @param {string} content - Content to copy
     */
    async copyToClipboard(content) {
      try {
        await navigator.clipboard.writeText(content);
        console.log('Content copied to clipboard');
        
        // Show a brief success message (optional)
        // You could add a toast notification here if desired
      } catch (error) {
        console.error('Failed to copy to clipboard:', error);
        
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = content;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        document.body.appendChild(textArea);
        textArea.select();
        try {
          document.execCommand('copy');
          console.log('Content copied to clipboard (fallback)');
        } catch (err) {
          console.error('Fallback copy failed:', err);
        }
        document.body.removeChild(textArea);
      }
    }

    /**
     * Load conversation history from API
     * Merges consecutive assistant messages into single messages
     */
    async loadConversationHistory() {
      const messages = await this.api.loadConversationHistory();

      if (messages && messages.length > 0) {
        // Group messages by conversation turn
        const turns = [];
        let currentTurn = null;
        
        for (let i = 0; i < messages.length; i++) {
          const msg = messages[i];
          
          if (!msg.content || typeof msg.content !== 'string') continue;
          
          const content = msg.content.trim();
          if (!content) continue;
          
          // Skip JSON array messages (tool calls - not rendered in history)
          let isJsonArray = false;
          try {
            const parsed = JSON.parse(content);
            isJsonArray = Array.isArray(parsed);
          } catch (e) {
            // Not valid JSON
          }
          if (isJsonArray) continue;
          
          if (msg.role === 'user') {
            currentTurn = {
              user: { content: content, id: msg.id },
              assistantTexts: []
            };
            turns.push(currentTurn);
          } else if (msg.role === 'assistant' && currentTurn) {
            currentTurn.assistantTexts.push(content);
          }
        }
        
        // Render each turn
        turns.forEach(turn => {
          // Render user message
          const userMessageId = turn.user.id || 'history_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
          this.ui.addMessage(turn.user.content, 'user', userMessageId);
          
          // Render merged assistant message
          if (turn.assistantTexts.length > 0) {
            const mergedText = turn.assistantTexts.join('\n\n');
            const assistantMessageId = 'history_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            const contentWithSuffix = mergedText + (this.i18n.helpSuffix || '');
            this.ui.addMessage(contentWithSuffix, 'assistant', assistantMessageId);
          }
        });

        if (turns.length > 0) {
          this.ui.scrollToBottom();
        }
      }
    }

    /**
     * Add welcome message based on API connection status
     */
    addWelcomeMessage() {
      this.ui.addWelcomeMessage(this.api.apiConnected);
    }

    /**
     * Send user message
     */
    async sendMessage() {
      const message = this.ui.getInputValue().trim();
      if (!message || this.ui.isTyping) return;

      // Add user message to UI
      this.ui.addMessage(message, 'user');
      this.ui.clearInput();

      // Create assistant message placeholder
      const assistantMessageDiv = this.ui.showTypingIndicator();
      const messageId = assistantMessageDiv.getAttribute('data-message-id') || 
                        `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      assistantMessageDiv.setAttribute('data-message-id', messageId);

      // Track active tool calls by call_id
      const activeToolCalls = new Map();

      try {
        // Get AI response with streaming
        await this.api.getAIResponseStream(
          message,
          // onContentUpdate
          (content) => {
            // Remove typing class when we start receiving content
            assistantMessageDiv.classList.remove('typing');
            this.ui.updateMessageContent(assistantMessageDiv, content);
          },
          // onToolUse
          (toolName, toolArgs, callId) => {
            // Remove typing indicator when first tool is called
            assistantMessageDiv.classList.remove('typing');
            // Clear the typing dots content
            const typingIndicator = assistantMessageDiv.querySelector('.typing-indicator');
            if (typingIndicator) {
              typingIndicator.remove();
            }
            
            // Add tool call to panel
            const toolId = this.ui.addToolCall(toolName, toolArgs, assistantMessageDiv);
            
            // Store mapping from callId to toolId
            if (callId) {
              activeToolCalls.set(callId, toolId);
            }
          },
          // onComplete
          (userMessage, assistantMessage) => {
            // Mark all remaining tools as done
            activeToolCalls.forEach(toolId => {
              this.ui.markToolCallDone(toolId);
            });
            
            // Ensure typing class is removed
            assistantMessageDiv.classList.remove('typing');
            // Remove the typingIndicator ID to prevent it from being deleted
            assistantMessageDiv.removeAttribute('id');
            
            // Extract content from assistantMessage
            let finalContent = '';
            if (typeof assistantMessage.content === 'string') {
              finalContent = assistantMessage.content;
            } else if (Array.isArray(assistantMessage.content)) {
              finalContent = assistantMessage.content
                .filter(c => c.type === "text")
                .map(c => c.text)
                .join('');
            }
            
            // Update with verified content and add helpSuffix at the end
            this.ui.finalizeMessage(assistantMessageDiv, finalContent);
            
            // Update with server-provided message ID
            if (assistantMessage.id) {
              assistantMessageDiv.setAttribute('data-message-id', assistantMessage.id);
            }

            const messageWrapper = assistantMessageDiv.parentNode;
            const hasFeedbackButtons = messageWrapper?.classList.contains('ask-ai-message-wrapper') && 
                                      messageWrapper.querySelector('.ask-ai-feedback-actions');
            
            if (!hasFeedbackButtons && assistantMessage.id) {
              console.log('Adding feedback buttons in onComplete');
              this.ui.addFeedbackButtons(assistantMessageDiv, assistantMessage.id, finalContent);
            } else if (hasFeedbackButtons) {
              // Update stored content for copying
              const feedbackDiv = messageWrapper.querySelector('.ask-ai-feedback-actions');
              if (feedbackDiv) {
                feedbackDiv.setAttribute('data-content', finalContent);
              }
            }
            
            // Mark typing as complete
            this.ui.isTyping = false;
            this.ui.sendBtn.disabled = false;
            
            // Store message with server ID
            this.ui.messages.push({
              content: finalContent,
              type: 'assistant',
              timestamp: Date.now(),
              messageId: assistantMessage.id
            });
          },
          // onError
          (error) => {
            assistantMessageDiv.classList.remove('typing');
            assistantMessageDiv.removeAttribute('id');
            this.ui.updateMessageContent(assistantMessageDiv, this.i18n.connectionError);
            this.ui.isTyping = false;
            this.ui.sendBtn.disabled = false;
            console.error('AI response error:', error);
          },
          // onToolComplete
          (callId) => {
            // Mark specific tool as done when its output is received
            const toolId = activeToolCalls.get(callId);
            if (toolId) {
              this.ui.markToolCallDone(toolId);
              console.log('Tool completed:', callId, '-> toolId:', toolId);
            }
          }
        );
      } catch (error) {
        assistantMessageDiv.classList.remove('typing');
        assistantMessageDiv.removeAttribute('id');
        this.ui.updateMessageContent(assistantMessageDiv, this.i18n.sendError);
        this.ui.isTyping = false;
        this.ui.sendBtn.disabled = false;
        console.error('Send message error:', error);
      }
    }


    /**
     * Clear conversation history
     */
    async clearConversation() {
      if (!confirm(this.i18n.clearConfirm)) {
        return;
      }

      const success = await this.api.clearConversation();

      if (success) {
        // Clear UI
        this.ui.clearMessages();

        // Add welcome message back
        this.addWelcomeMessage();

        console.log('Conversation cleared successfully');
      } else {
        alert(this.i18n.clearFailed);
      }
    }
  }

  // Initialize the widget when DOM is loaded
  document.addEventListener('DOMContentLoaded', async () => {
    // Check if we're in a Sphinx documentation page
    if (document.body.classList.contains('furo') || document.querySelector('.furo')) {
      new AskAIWidget();
    } else {
      // Fallback for other themes
      setTimeout(() => {
        new AskAIWidget();
      }, 1000);
    }
  });

  // Export for potential external usage
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = AskAIWidget;
  }

  return AskAIWidget;

})();
