with open("src/index.css", "a", encoding="utf-8") as f:
    f.write('''
/* Extra specific card styles */
.mission-card {
  background: var(--page-bg);
  border: 1px solid var(--card-border);
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 0.75rem;
  display: flex;
  flex-direction: column;
}

.mission-card.ack {
  border-left: 4px solid var(--status-healthy);
}

.mission-card.unack {
  border-left: 4px solid var(--status-warning);
}

.mission-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.directive-from { color: var(--text-heading); font-weight: 600; }
.directive-time { color: var(--text-muted); font-size: 0.85rem; }
.directive-msg { margin: 0; line-height: 1.5; color: var(--text-main); }

.checkout-form-container, .plan-form-container {
  background: var(--page-bg);
  border: 1px solid var(--card-border);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-grid input, .form-grid textarea, .form-grid select {
  padding: 0.5rem;
  border: 1px solid var(--card-border);
  border-radius: 4px;
  font-family: inherit;
  width: 100%;
}
''')
print("Added CSS.")
