/**
 * Ask AI Widget - UI Management Module
 */

export class AskAIUI {
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
        const currentSegmentText = lastContentSegment.textContent || '';
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