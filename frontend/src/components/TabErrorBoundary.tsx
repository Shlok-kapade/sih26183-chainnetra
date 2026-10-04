import { Component, type ReactNode } from 'react';

export class TabErrorBoundary extends Component<{ children: ReactNode; resetKey?: string }, { error: Error | null; key?: string }> {
  state = { error: null as Error | null, key: this.props.resetKey };

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  componentDidUpdate(prev: { resetKey?: string }) {
    if (prev.resetKey !== this.props.resetKey && this.state.error) {
      this.setState({ error: null });
    }
  }

  render() {
    if (this.state.error) {
      return (
        <div className="p-6 text-sm text-red-700 bg-red-50 border border-red-200 rounded m-4">
          This tab failed to render: {this.state.error.message}
        </div>
      );
    }
    return this.props.children;
  }
}
