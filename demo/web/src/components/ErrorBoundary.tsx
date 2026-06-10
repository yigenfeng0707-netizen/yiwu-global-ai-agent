import { Component, type ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;
      return (
        <div className="flex flex-col items-center justify-center py-20 space-y-4">
          <AlertTriangle size={40} className="text-gold-500" />
          <h3 className="text-lg font-medium text-white">页面出错了</h3>
          <p className="text-sm text-gray-400 max-w-md text-center">
            {this.state.error?.message || '发生了未知错误，请稍后重试'}
          </p>
          <button
            onClick={this.handleRetry}
            className="rounded-lg bg-yiwu-600 px-5 py-2 text-sm font-medium text-white hover:bg-yiwu-500 transition-colors flex items-center gap-2"
          >
            <RefreshCw size={14} /> 重试
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
