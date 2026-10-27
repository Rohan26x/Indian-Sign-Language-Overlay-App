/**
 * CardSequencerUI (Sections 4.2.1–4.2.4):
 * Manages 2D Visual Sign Cards, Emojis, and Fingerspelling Tickers.
 * Preserves visual card rendering alongside 3D avatar in Dual-Mode / Hybrid display.
 */

class CardSequencerUI {
  constructor(stageElement, ribbonBadgesElement) {
    this.stage = stageElement;
    this.badgesContainer = ribbonBadgesElement;
    this.playbackSpeed = 1.0;
    this.queue = [];
    this.timer = null;
    this.activeBadgeIndex = 0;
    this.badgeElements = [];
  }

  setSpeed(speed) {
    this.playbackSpeed = Math.max(0.5, Math.min(2.0, speed));
  }

  renderCard(data) {
    const isFingerspelling = data.fingerspelling || data.category === 'FINGERSPELLING';
    const badgeCategory = isFingerspelling ? 'FINGERSPELLING' : (data.category || 'SIGN');
    const emojiIcon = data.emoji || (isFingerspelling ? '🔤' : '🤟');

    this.stage.innerHTML = `
      <div class="active-card ${isFingerspelling ? 'fingerspelling-card' : ''}">
        <div class="card-emoji">${emojiIcon}</div>
        <div class="card-gloss">${data.display_text || data.gloss}</div>
        <div class="card-category">${badgeCategory}</div>
      </div>
    `;
  }

  clearCard() {
    this.stage.innerHTML = '';
  }

  enqueueSequence(sequence) {
    if (!sequence || sequence.length === 0) return;
    this.queue.push(...sequence);

    // Refresh gloss badges ribbon
    this.badgesContainer.innerHTML = '';
    this.badgeElements = [];
    sequence.forEach((item, idx) => {
      const badge = document.createElement('span');
      badge.className = 'gloss-badge';
      badge.textContent = item.display_text || item.gloss;
      badge.title = `Category: ${item.category || 'SIGN'}`;
      this.badgesContainer.appendChild(badge);
      this.badgeElements.push(badge);
    });

    this.activeBadgeIndex = 0;

    if (!this.timer) {
      this.playNext();
    }
  }

  playNext() {
    if (this.queue.length === 0) {
      this.timer = setTimeout(() => {
        this.clearCard();
        this.timer = null;
        if (this.badgeElements.length > 0) {
          this.badgeElements.forEach(b => b.classList.remove('active-gloss'));
        }
      }, 1000 / this.playbackSpeed);
      return;
    }

    // Adaptive Backpressure for Cards: scale speed if queue has backlog
    let effectiveSpeed = this.playbackSpeed;
    if (this.queue.length >= 4) {
      effectiveSpeed = Math.min(1.5, this.playbackSpeed * 1.35);
    }

    const item = this.queue.shift();
    this.renderCard(item);

    // Highlight current gloss badge
    if (this.badgeElements[this.activeBadgeIndex]) {
      this.badgeElements.forEach(b => b.classList.remove('active-gloss'));
      this.badgeElements[this.activeBadgeIndex].classList.add('active-gloss');
      this.activeBadgeIndex++;
    }

    const baseDuration = (item.fingerspelling || item.category === 'FINGERSPELLING') ? 500 : 850;
    const displayDuration = baseDuration / effectiveSpeed;

    this.timer = setTimeout(() => {
      this.playNext();
    }, displayDuration);
  }
}
