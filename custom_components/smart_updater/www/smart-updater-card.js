import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element.js?module";

class SmartUpdaterCard extends LitElement {
  static get properties() {
    return {
      hass: {},
      config: {},
      selected_updates: [],
    };
  }

  constructor() {
    super();
    this.selected_updates = [];
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error("You need to define an entity");
    }
    this.config = config;
  }

  render() {
    const state = this.hass.states[this.config.entity];
    if (!state) {
      return html`
        <ha-card>
          <div class="card-content">
            Entity not found: ${this.config.entity}
          </div>
        </ha-card>
      `;
    }

    const updates = state.attributes.updates || [];
    const history = state.attributes.history || [];

    return html`
      <ha-card header="Smart Updater">
        <div class="card-content">
          <h3>${state.state} updates available</h3>
          ${updates.length > 0
            ? this._renderUpdates(updates)
            : html`<p>No updates available.</p>`}
        </div>
        ${updates.length > 0
          ? html`
              <div class="card-actions">
                <mwc-button @click=${this._updateSelected}>
                  Update Selected
                </mwc-button>
              </div>
            `
          : ""}

        <div class="card-content">
          <h3>Update History</h3>
          ${history.length > 0
            ? this._renderHistory(history)
            : html`<p>No update history.</p>`}
        </div>
      </ha-card>
    `;
  }

  _renderUpdates(updates) {
    return html`
      <table>
        <thead>
          <tr>
            <th></th>
            <th>Name</th>
            <th>Installed</th>
            <th>Available</th>
          </tr>
        </thead>
        <tbody>
          ${updates.map(
            (update) => html`
              <tr>
                <td>
                  <input
                    type="checkbox"
                    .value=${update.entity_id}
                    @change=${this._handleCheckboxChange}
                  />
                </td>
                <td>${update.name}</td>
                <td>${update.installed_version}</td>
                <td>${update.latest_version}</td>
              </tr>
            `
          )}
        </tbody>
      </table>
    `;
  }

  _renderHistory(history) {
    return html`
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>From</th>
            <th>To</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          ${history.map(
            (item) => html`
              <tr>
                <td>${item.name}</td>
                <td>${item.old_version}</td>
                <td>${item.new_version}</td>
                <td>${new Date(item.timestamp).toLocaleString()}</td>
              </tr>
            `
          )}
        </tbody>
      </table>
    `;
  }

  _handleCheckboxChange(e) {
    const entity_id = e.target.value;
    if (e.target.checked) {
      this.selected_updates.push(entity_id);
    } else {
      this.selected_updates = this.selected_updates.filter(
        (id) => id !== entity_id
      );
    }
  }

  _updateSelected() {
    this.hass.callService("smart_updater", "update_selected", {
      entity_id: this.selected_updates,
    });
  }

  getCardSize() {
    const state = this.hass.states[this.config.entity];
    if (!state) {
      return 1;
    }
    const updates = state.attributes.updates || [];
    const history = state.attributes.history || [];
    return updates.length + history.length + 3; // +1 for each header, +1 for button
  }

  static get styles() {
    return css`
      table {
        width: 100%;
        border-collapse: collapse;
      }
      th,
      td {
        text-align: left;
        padding: 8px;
        border-bottom: 1px solid #ddd;
      }
      .card-actions {
        padding: 8px;
        display: flex;
        justify-content: flex-end;
      }
    `;
  }
}

customElements.define("smart-updater-card", SmartUpdaterCard);
