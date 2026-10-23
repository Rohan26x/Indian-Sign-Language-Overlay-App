/**
 * CardSequencerUI: Handles 2D Visual Sign Cards, Emojis, and Fingerspelling Tickers.
 */

class CardSequencerUI {
  constructor(stageElement, ribbonBadgesElement) {
    this.stage = stageElement;
    this.badgesContainer = ribbonBadgesElement;
    this.playbackSpeed = 1.0;
    this.queue = [];
    this.timer = null;
    this.currentCard = null;
  }

  setSpeed(speed) {
    this.playbackSpeed = Math.max(0.5, Math.min(2.0, speed));
  }

  renderCard(data) {
    this.stage.innerHTML = `
      <div class="active-card">
        <div class="card-emoji">${data.emoji || '🔤'}</div>
        <div class="card-gloss">${data.display_text || data.gloss}</div>
        <div class="card-category">${data.category || 'SIGN'}</div>
      </div>
    `;
  }

  clearCard() {
    this.stage.innerHTML = '';
  }

  enqueueSequence(sequence) {
    if (!sequence || sequence.length === 0) return;
    this.queue.push(...sequence);

    // Update bottom gloss badges
    this.badgesContainer.innerHTML = '';
    sequence.forEach((item) => {
      const badge = document.createElement('span');
      badge.className = 'gloss-badge';
      badge.textContent = item.display_text || item.gloss;
      this.badgesContainer.appendChild(badge);
    });

    if (!this.timer) {
      this.playNext();
    }
  }

  playNext() {
    if (this.queue.length === 0) {
      this.timer = setTimeout(() => {
        this.clearCard();
        this.timer = null;
      }, 1200 / this.playbackSpeed);
      return;
    }

    const item = this.queue.shift();
    this.renderCard(item);

    const displayDuration = (item.fingerspelling ? 600 : 900) / this.playbackSpeed;
    this.timer = setTimeout(() => {
      this.playNext();
    }, displayDuration);
  }
}
