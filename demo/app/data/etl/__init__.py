"""义乌小商品出海智能体 - 真实数据源 ETL 包（P1-1 真数据源样板）

对外暴露：
  - FetchResult / RealDataSource：ETL 抽象与标准化产物
  - ExchangeRateSource：源A 每日参考汇率（保证可现场自证）
  - YiwuIndexSource：源B 义乌指数官方发布值（叙事皇冠）
  - RealDataRegistry / get_registry：真实源注册表（刷新/状态/三态回退）
  - DataSourceStatus：数据源真/演示/规划三态状态

设计目标（对应《升级改造方案》P1-1）：
  把"全静态假数据 + random"升级为"1+ 个真实可跑的数据源样板 + 其余明确标注规划/演示"，
  每个真实源都带 source_url + fetched_at，评委可现场复核请求-响应。
"""

from .base import FetchResult, RealDataSource
from .exchange_rate import ExchangeRateSource
from .yiwu_index import YiwuIndexSource
from .yixinou import YixinouSource
from .registry import RealDataRegistry, get_registry, DataSourceStatus

__all__ = [
    "FetchResult",
    "RealDataSource",
    "ExchangeRateSource",
    "YiwuIndexSource",
    "YixinouSource",
    "RealDataRegistry",
    "get_registry",
    "DataSourceStatus",
]
