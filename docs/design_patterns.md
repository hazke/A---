# 设计模式说明文档

本文档详细说明了A股量化交易系统中使用的各种设计模式及其应用场景。

## 1. 策略模式 (Strategy Pattern)

### 应用位置
- `core/strategy/base_strategy.py` - 策略基类
- `strategies/moving_average_strategy.py` - 具体策略实现

### 设计目的
允许在运行时选择算法，将算法的定义、创建、使用解耦。

### 实现方式
```python
# 策略基类定义接口
class BaseStrategy(ABC):
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

# 具体策略实现
class MovingAverageStrategy(BaseStrategy):
    def generate_signals(self, data: pd.DataFrame):
        # 实现移动平均策略逻辑
        pass
```

### 优势
- 易于添加新策略，只需继承`BaseStrategy`
- 策略之间相互独立，互不影响
- 符合开闭原则（对扩展开放，对修改关闭）

---

## 2. 工厂模式 (Factory Pattern)

### 应用位置
- `core/factory/data_factory.py` - 数据源工厂
- `core/factory/strategy_factory.py` - 策略工厂

### 设计目的
封装对象的创建过程，客户端不需要知道具体创建哪个类的实例。

### 实现方式
```python
# 数据源工厂
class DataFactory:
    @staticmethod
    def create_adapter(source_type: str = None) -> DataAdapter:
        if source_type == 'tushare':
            return TushareAdapter()
        elif source_type == 'akshare':
            return AKShareAdapter()

# 使用
adapter = DataFactory.create_adapter('tushare')
```

### 优势
- 统一创建接口，简化客户端代码
- 易于扩展新的数据源或策略类型
- 集中管理对象创建逻辑

---

## 3. 适配器模式 (Adapter Pattern)

### 应用位置
- `core/data/data_adapter.py` - 适配器基类
- `core/data/tushare_adapter.py` - Tushare适配器
- `core/data/akshare_adapter.py` - AKShare适配器

### 设计目的
将不同数据源的接口转换为统一的接口，使不兼容的接口可以协同工作。

### 实现方式
```python
# 统一接口
class DataAdapter(ABC):
    @abstractmethod
    def get_daily_data(self, stock_code: str, start_date: str, end_date: str):
        pass

# 不同数据源的适配器实现统一接口
class TushareAdapter(DataAdapter):
    def get_daily_data(self, stock_code: str, start_date: str, end_date: str):
        # Tushare特定的实现
        pass

class AKShareAdapter(DataAdapter):
    def get_daily_data(self, stock_code: str, start_date: str, end_date: str):
        # AKShare特定的实现
        pass
```

### 优势
- 统一数据接口，策略代码无需关心数据来源
- 可以轻松切换数据源
- 符合依赖倒置原则

---

## 4. 观察者模式 (Observer Pattern)

### 应用位置
- `core/observer/observer.py`

### 设计目的
定义对象间一对多的依赖关系，当一个对象状态改变时，所有依赖它的对象都会得到通知。

### 实现方式
```python
# 观察者接口
class Observer(ABC):
    @abstractmethod
    def update(self, event_type: str, data: Dict):
        pass

# 主题（被观察者）
class MarketDataSubject(Subject):
    def update_price(self, stock_code: str, price: float):
        self.notify('price_update', {'stock_code': stock_code, 'price': price})

# 具体观察者
class LoggingObserver(Observer):
    def update(self, event_type: str, data: Dict):
        # 记录日志
        pass
```

### 应用场景
- 实时行情数据推送
- 交易执行通知
- 价格警报触发
- 系统事件日志记录

### 优势
- 解耦观察者和被观察者
- 支持动态添加/移除观察者
- 符合开闭原则

---

## 5. 命令模式 (Command Pattern)

### 应用位置
- `core/execution/order_command.py`

### 设计目的
将请求封装为对象，从而可以用不同的请求对客户进行参数化，支持请求的排队、记录、撤销等操作。

### 实现方式
```python
# 命令接口
class OrderCommand(ABC):
    @abstractmethod
    def execute(self) -> bool:
        pass
    
    @abstractmethod
    def cancel(self) -> bool:
        pass

# 具体命令
class BuyOrder(OrderCommand):
    def execute(self) -> bool:
        # 执行买入
        pass

class SellOrder(OrderCommand):
    def execute(self) -> bool:
        # 执行卖出
        pass

# 调用者
class OrderInvoker:
    def execute_order(self, order: OrderCommand):
        order.execute()
```

### 应用场景
- 订单执行和撤销
- 交易历史记录
- 订单回滚操作
- 批量订单处理

### 优势
- 将请求封装为对象，易于扩展
- 支持撤销操作
- 可以记录命令历史，实现回放功能

---

## 6. 单例模式 (Singleton Pattern)

### 应用位置
- `core/config_manager.py`

### 设计目的
确保一个类只有一个实例，并提供全局访问点。

### 实现方式
```python
class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
```

### 应用场景
- 配置管理器（全局唯一配置）
- 日志管理器
- 数据库连接池

### 优势
- 确保配置的唯一性
- 节省内存资源
- 提供全局访问点

---

## 7. 模板方法模式 (Template Method Pattern)

### 应用位置
- `core/strategy/base_strategy.py` - `run()`方法

### 设计目的
定义算法骨架，将一些步骤延迟到子类中，使得子类可以不改变算法结构即可重定义某些步骤。

### 实现方式
```python
class BaseStrategy(ABC):
    def run(self, data: pd.DataFrame):
        # 1. 初始化（固定流程）
        self.on_init()
        
        # 2. 数据预处理（子类实现）
        processed_data = self.preprocess_data(data)
        
        # 3. 生成信号（子类实现）
        signals = self.generate_signals(processed_data)
        
        # 4. 执行交易（固定流程，子类可重写）
        trades = self.execute_trades(signals)
        
        # 5. 风险控制（固定流程）
        self.risk_control()
        
        # 6. 结束处理（固定流程）
        return self.on_finish()
```

### 优势
- 代码复用，避免重复
- 控制子类扩展点
- 统一策略执行流程

---

## 设计模式组合使用

在实际应用中，这些设计模式经常组合使用：

1. **工厂模式 + 策略模式**：工厂创建策略实例，策略模式实现不同算法
2. **适配器模式 + 工厂模式**：工厂创建适配器，适配器统一不同数据源
3. **观察者模式 + 命令模式**：命令执行时通知观察者
4. **模板方法模式 + 策略模式**：模板方法定义流程，策略模式实现具体算法

## 扩展建议

### 可以添加的设计模式

1. **责任链模式**：用于风险控制的多级检查
2. **状态模式**：订单状态管理（待成交、已成交、已撤销等）
3. **装饰器模式**：为策略添加额外的功能（如日志、性能监控）
4. **代理模式**：数据缓存代理，减少API调用

## 总结

通过合理使用这些设计模式，系统具有以下特点：
- ✅ **可扩展性**：易于添加新策略、新数据源
- ✅ **可维护性**：代码结构清晰，职责分明
- ✅ **可测试性**：模块解耦，便于单元测试
- ✅ **灵活性**：运行时动态选择策略和数据源

