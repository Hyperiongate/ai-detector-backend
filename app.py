import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import os
import time
import re
from collections import defaultdict
import hashlib
import hmac
import sqlite3
from typing import Dict, List, Tuple, Optional, Union, Any
import logging
from dataclasses import dataclass, field
from enum import Enum
import uuid
import pytz
from functools import wraps
import traceback
import io
import base64
from PIL import Image
import requests
from urllib.parse import urlparse, parse_qs
import subprocess
import sys
import tempfile
import shutil
import zipfile
import csv
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
APP_VERSION = "2.0.0"
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
SUPPORTED_FILE_TYPES = ['.csv', '.xlsx', '.xls', '.json', '.parquet', '.tsv']
BATCH_SIZE = 10000
CACHE_TTL = 3600  # 1 hour
DEFAULT_TIMEZONE = 'UTC'

# Color schemes
COLOR_SCHEMES = {
    'default': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'],
    'pastel': ['#FFB6C1', '#87CEEB', '#DDA0DD', '#F0E68C', '#98FB98',
               '#F4A460', '#D8BFD8', '#B0E0E6', '#FFDAB9', '#E0FFFF'],
    'dark': ['#2E4053', '#1A5276', '#512E5F', '#7D3C98', '#A04000',
             '#B7950B', '#1E8449', '#148F77', '#17202A', '#641E16'],
    'vibrant': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57',
                '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2']
}

# Data type mappings
DATA_TYPE_MAPPINGS = {
    'int64': 'Integer',
    'float64': 'Float',
    'object': 'String',
    'datetime64': 'DateTime',
    'bool': 'Boolean',
    'category': 'Category',
    'timedelta64': 'TimeDelta'
}

# Enums
class ChartType(Enum):
    LINE = "Line Chart"
    BAR = "Bar Chart"
    SCATTER = "Scatter Plot"
    PIE = "Pie Chart"
    HISTOGRAM = "Histogram"
    BOX = "Box Plot"
    HEATMAP = "Heatmap"
    AREA = "Area Chart"
    VIOLIN = "Violin Plot"
    SUNBURST = "Sunburst"
    TREEMAP = "Treemap"
    WATERFALL = "Waterfall"
    FUNNEL = "Funnel"
    GAUGE = "Gauge"
    RADAR = "Radar"
    SANKEY = "Sankey"
    CANDLESTICK = "Candlestick"
    PARALLEL = "Parallel Coordinates"
    SCATTER_3D = "3D Scatter"
    SURFACE_3D = "3D Surface"

class AggregationType(Enum):
    SUM = "sum"
    MEAN = "mean"
    MEDIAN = "median"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    UNIQUE = "nunique"
    STD = "std"
    VAR = "var"
    FIRST = "first"
    LAST = "last"

class FilterOperator(Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not equals"
    GREATER = "greater than"
    LESS = "less than"
    GREATER_EQUAL = "greater or equal"
    LESS_EQUAL = "less or equal"
    CONTAINS = "contains"
    NOT_CONTAINS = "not contains"
    STARTS_WITH = "starts with"
    ENDS_WITH = "ends with"
    IN = "in"
    NOT_IN = "not in"
    BETWEEN = "between"
    IS_NULL = "is null"
    IS_NOT_NULL = "is not null"

# Data classes
@dataclass
class DataSource:
    id: str
    name: str
    type: str
    path: str
    columns: List[str]
    row_count: int
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Chart:
    id: str
    name: str
    type: ChartType
    data_source_id: str
    config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class Dashboard:
    id: str
    name: str
    charts: List[str]
    layout: Dict[str, Any]
    filters: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class User:
    id: str
    username: str
    email: str
    role: str
    created_at: datetime
    last_login: datetime
    preferences: Dict[str, Any] = field(default_factory=dict)

# Decorators
def timer(func):
    """Decorator to time function execution"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.info(f"{func.__name__} took {end - start:.2f} seconds")
        return result
    return wrapper

def error_handler(func):
    """Decorator to handle errors gracefully"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            st.error(f"An error occurred: {str(e)}")
            return None
    return wrapper

def cache_result(ttl=CACHE_TTL):
    """Decorator to cache function results"""
    def decorator(func):
        cache = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = hashlib.md5(
                f"{func.__name__}_{args}_{kwargs}".encode()
            ).hexdigest()
            
            if key in cache:
                result, timestamp = cache[key]
                if time.time() - timestamp < ttl:
                    return result
            
            result = func(*args, **kwargs)
            cache[key] = (result, time.time())
            return result
        
        return wrapper
    return decorator

# Database functions
class DatabaseManager:
    def __init__(self, db_path='dataviz_app.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Data sources table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_sources (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    path TEXT NOT NULL,
                    columns TEXT NOT NULL,
                    row_count INTEGER NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    metadata TEXT
                )
            ''')
            
            # Charts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS charts (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    data_source_id TEXT NOT NULL,
                    config TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (data_source_id) REFERENCES data_sources(id)
                )
            ''')
            
            # Dashboards table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dashboards (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    charts TEXT NOT NULL,
                    layout TEXT NOT NULL,
                    filters TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    metadata TEXT
                )
            ''')
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    last_login TIMESTAMP,
                    preferences TEXT
                )
            ''')
            
            # Audit log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    action TEXT NOT NULL,
                    object_type TEXT,
                    object_id TEXT,
                    timestamp TIMESTAMP NOT NULL,
                    details TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            conn.commit()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Any]:
        """Execute a SELECT query"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE query"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.lastrowid
    
    def save_data_source(self, data_source: DataSource) -> bool:
        """Save a data source to the database"""
        try:
            self.execute_update(
                '''INSERT OR REPLACE INTO data_sources 
                   (id, name, type, path, columns, row_count, created_at, updated_at, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (data_source.id, data_source.name, data_source.type, data_source.path,
                 json.dumps(data_source.columns), data_source.row_count,
                 data_source.created_at, data_source.updated_at,
                 json.dumps(data_source.metadata))
            )
            return True
        except Exception as e:
            logger.error(f"Error saving data source: {e}")
            return False
    
    def get_data_source(self, source_id: str) -> Optional[DataSource]:
        """Get a data source by ID"""
        results = self.execute_query(
            "SELECT * FROM data_sources WHERE id = ?", (source_id,)
        )
        
        if results:
            row = results[0]
            return DataSource(
                id=row['id'],
                name=row['name'],
                type=row['type'],
                path=row['path'],
                columns=json.loads(row['columns']),
                row_count=row['row_count'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                metadata=json.loads(row['metadata']) if row['metadata'] else {}
            )
        return None
    
    def save_chart(self, chart: Chart) -> bool:
        """Save a chart to the database"""
        try:
            self.execute_update(
                '''INSERT OR REPLACE INTO charts 
                   (id, name, type, data_source_id, config, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (chart.id, chart.name, chart.type.value, chart.data_source_id,
                 json.dumps(chart.config), chart.created_at, chart.updated_at)
            )
            return True
        except Exception as e:
            logger.error(f"Error saving chart: {e}")
            return False
    
    def log_action(self, user_id: str, action: str, object_type: str = None,
                   object_id: str = None, details: Dict[str, Any] = None):
        """Log an action to the audit log"""
        self.execute_update(
            '''INSERT INTO audit_log (user_id, action, object_type, object_id, timestamp, details)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (user_id, action, object_type, object_id, datetime.now(),
             json.dumps(details) if details else None)
        )

# Data processing functions
class DataProcessor:
    @staticmethod
    @timer
    def load_file(file_path: str, file_type: str = None) -> pd.DataFrame:
        """Load data from various file formats"""
        if file_type is None:
            file_type = Path(file_path).suffix.lower()
        
        try:
            if file_type in ['.csv', '.tsv']:
                delimiter = '\t' if file_type == '.tsv' else ','
                df = pd.read_csv(file_path, delimiter=delimiter, low_memory=False)
            elif file_type in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            elif file_type == '.json':
                df = pd.read_json(file_path)
            elif file_type == '.parquet':
                df = pd.read_parquet(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            return df
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            raise
    
    @staticmethod
    def detect_data_types(df: pd.DataFrame) -> Dict[str, str]:
        """Detect and optimize data types"""
        type_mapping = {}
        
        for col in df.columns:
            col_type = str(df[col].dtype)
            
            # Try to convert object columns to more specific types
            if col_type == 'object':
                # Check if it's a date
                try:
                    pd.to_datetime(df[col], errors='coerce')
                    if df[col].notna().sum() > 0:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                        col_type = 'datetime64'
                except:
                    pass
                
                # Check if it's numeric
                if col_type == 'object':
                    try:
                        numeric_series = pd.to_numeric(df[col], errors='coerce')
                        if numeric_series.notna().sum() / len(df) > 0.5:
                            df[col] = numeric_series
                            col_type = str(df[col].dtype)
                    except:
                        pass
            
            type_mapping[col] = DATA_TYPE_MAPPINGS.get(col_type, col_type)
        
        return type_mapping
    
    @staticmethod
    def clean_data(df: pd.DataFrame, options: Dict[str, Any]) -> pd.DataFrame:
        """Clean and preprocess data"""
        df_clean = df.copy()
        
        # Remove duplicates
        if options.get('remove_duplicates', True):
            df_clean = df_clean.drop_duplicates()
        
        # Handle missing values
        if options.get('handle_missing', True):
            strategy = options.get('missing_strategy', 'drop')
            
            if strategy == 'drop':
                df_clean = df_clean.dropna()
            elif strategy == 'fill_mean':
                numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
                df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].mean())
            elif strategy == 'fill_median':
                numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
                df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].median())
            elif strategy == 'fill_forward':
                df_clean = df_clean.fillna(method='ffill')
            elif strategy == 'fill_backward':
                df_clean = df_clean.fillna(method='bfill')
        
        # Remove outliers
        if options.get('remove_outliers', False):
            numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
            z_threshold = options.get('outlier_threshold', 3)
            
            for col in numeric_cols:
                z_scores = np.abs((df_clean[col] - df_clean[col].mean()) / df_clean[col].std())
                df_clean = df_clean[z_scores < z_threshold]
        
        return df_clean
    
    @staticmethod
    def aggregate_data(df: pd.DataFrame, group_by: List[str], 
                      agg_config: Dict[str, str]) -> pd.DataFrame:
        """Aggregate data based on configuration"""
        agg_dict = {}
        
        for col, agg_type in agg_config.items():
            if col in df.columns and col not in group_by:
                agg_dict[col] = agg_type
        
        if not agg_dict:
            return df
        
        return df.groupby(group_by).agg(agg_dict).reset_index()
    
    @staticmethod
    def filter_data(df: pd.DataFrame, filters: List[Dict[str, Any]]) -> pd.DataFrame:
        """Apply filters to dataframe"""
        df_filtered = df.copy()
        
        for filter_config in filters:
            col = filter_config['column']
            op = FilterOperator(filter_config['operator'])
            value = filter_config['value']
            
            if col not in df.columns:
                continue
            
            if op == FilterOperator.EQUALS:
                df_filtered = df_filtered[df_filtered[col] == value]
            elif op == FilterOperator.NOT_EQUALS:
                df_filtered = df_filtered[df_filtered[col] != value]
            elif op == FilterOperator.GREATER:
                df_filtered = df_filtered[df_filtered[col] > value]
            elif op == FilterOperator.LESS:
                df_filtered = df_filtered[df_filtered[col] < value]
            elif op == FilterOperator.GREATER_EQUAL:
                df_filtered = df_filtered[df_filtered[col] >= value]
            elif op == FilterOperator.LESS_EQUAL:
                df_filtered = df_filtered[df_filtered[col] <= value]
            elif op == FilterOperator.CONTAINS:
                df_filtered = df_filtered[df_filtered[col].astype(str).str.contains(value, na=False)]
            elif op == FilterOperator.NOT_CONTAINS:
                df_filtered = df_filtered[~df_filtered[col].astype(str).str.contains(value, na=False)]
            elif op == FilterOperator.STARTS_WITH:
                df_filtered = df_filtered[df_filtered[col].astype(str).str.startswith(value, na=False)]
            elif op == FilterOperator.ENDS_WITH:
                df_filtered = df_filtered[df_filtered[col].astype(str).str.endswith(value, na=False)]
            elif op == FilterOperator.IN:
                df_filtered = df_filtered[df_filtered[col].isin(value)]
            elif op == FilterOperator.NOT_IN:
                df_filtered = df_filtered[~df_filtered[col].isin(value)]
            elif op == FilterOperator.BETWEEN:
                df_filtered = df_filtered[df_filtered[col].between(value[0], value[1])]
            elif op == FilterOperator.IS_NULL:
                df_filtered = df_filtered[df_filtered[col].isna()]
            elif op == FilterOperator.IS_NOT_NULL:
                df_filtered = df_filtered[df_filtered[col].notna()]
        
        return df_filtered
    
    @staticmethod
    def calculate_statistics(df: pd.DataFrame, columns: List[str] = None) -> Dict[str, Any]:
        """Calculate comprehensive statistics for numeric columns"""
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        stats = {}
        
        for col in columns:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                col_stats = {
                    'count': int(df[col].count()),
                    'mean': float(df[col].mean()),
                    'median': float(df[col].median()),
                    'mode': float(df[col].mode()[0]) if len(df[col].mode()) > 0 else None,
                    'std': float(df[col].std()),
                    'var': float(df[col].var()),
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'q1': float(df[col].quantile(0.25)),
                    'q3': float(df[col].quantile(0.75)),
                    'iqr': float(df[col].quantile(0.75) - df[col].quantile(0.25)),
                    'skewness': float(df[col].skew()),
                    'kurtosis': float(df[col].kurtosis()),
                    'null_count': int(df[col].isna().sum()),
                    'null_percentage': float(df[col].isna().sum() / len(df) * 100)
                }
                stats[col] = col_stats
        
        return stats
    
    @staticmethod
    def pivot_data(df: pd.DataFrame, index: List[str], columns: List[str],
                   values: str, aggfunc: str = 'mean') -> pd.DataFrame:
        """Create pivot table from dataframe"""
        return pd.pivot_table(
            df,
            index=index,
            columns=columns,
            values=values,
            aggfunc=aggfunc,
            fill_value=0
        ).reset_index()
    
    @staticmethod
    def sample_data(df: pd.DataFrame, sample_size: int = None,
                    sample_frac: float = None, random_state: int = 42) -> pd.DataFrame:
        """Sample data from dataframe"""
        if sample_size is not None:
            return df.sample(n=min(sample_size, len(df)), random_state=random_state)
        elif sample_frac is not None:
            return df.sample(frac=sample_frac, random_state=random_state)
        else:
            return df

# Visualization functions
class ChartBuilder:
    def __init__(self, theme: str = 'plotly'):
        self.theme = theme
        self.color_scheme = COLOR_SCHEMES['default']
    
    def set_color_scheme(self, scheme: str):
        """Set color scheme for charts"""
        if scheme in COLOR_SCHEMES:
            self.color_scheme = COLOR_SCHEMES[scheme]
    
    def create_line_chart(self, df: pd.DataFrame, x: str, y: Union[str, List[str]],
                         title: str = "", **kwargs) -> go.Figure:
        """Create a line chart"""
        fig = go.Figure()
        
        if isinstance(y, str):
            y = [y]
        
        for i, col in enumerate(y):
            fig.add_trace(go.Scatter(
                x=df[x],
                y=df[col],
                mode='lines+markers',
                name=col,
                line=dict(color=self.color_scheme[i % len(self.color_scheme)]),
                **kwargs
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x,
            yaxis_title=', '.join(y) if len(y) > 1 else y[0],
            template=self.theme,
            hovermode='x unified'
        )
        
        return fig
    
    def create_bar_chart(self, df: pd.DataFrame, x: str, y: Union[str, List[str]],
                        title: str = "", orientation: str = 'v', **kwargs) -> go.Figure:
        """Create a bar chart"""
        fig = go.Figure()
        
        if isinstance(y, str):
            y = [y]
        
        for i, col in enumerate(y):
            fig.add_trace(go.Bar(
                x=df[x] if orientation == 'v' else df[col],
                y=df[col] if orientation == 'v' else df[x],
                name=col,
                orientation=orientation,
                marker_color=self.color_scheme[i % len(self.color_scheme)],
                **kwargs
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x if orientation == 'v' else ', '.join(y),
            yaxis_title=', '.join(y) if orientation == 'v' else x,
            template=self.theme,
            barmode=kwargs.get('barmode', 'group')
        )
        
        return fig
    
    def create_scatter_plot(self, df: pd.DataFrame, x: str, y: str,
                           size: str = None, color: str = None,
                           title: str = "", **kwargs) -> go.Figure:
        """Create a scatter plot"""
        fig = px.scatter(
            df, x=x, y=y, size=size, color=color,
            title=title, template=self.theme,
            color_discrete_sequence=self.color_scheme,
            **kwargs
        )
        
        return fig
    
    def create_pie_chart(self, df: pd.DataFrame, values: str, names: str,
                        title: str = "", **kwargs) -> go.Figure:
        """Create a pie chart"""
        fig = go.Figure(data=[go.Pie(
            values=df[values],
            labels=df[names],
            marker=dict(colors=self.color_scheme),
            **kwargs
        )])
        
        fig.update_layout(title=title, template=self.theme)
        
        return fig
    
    def create_histogram(self, df: pd.DataFrame, x: str, nbins: int = 30,
                        title: str = "", **kwargs) -> go.Figure:
        """Create a histogram"""
        fig = go.Figure(data=[go.Histogram(
            x=df[x],
            nbinsx=nbins,
            marker_color=self.color_scheme[0],
            **kwargs
        )])
        
        fig.update_layout(
            title=title,
            xaxis_title=x,
            yaxis_title='Count',
            template=self.theme
        )
        
        return fig
    
    def create_box_plot(self, df: pd.DataFrame, y: str, x: str = None,
                       title: str = "", **kwargs) -> go.Figure:
        """Create a box plot"""
        if x:
            fig = px.box(df, x=x, y=y, title=title, template=self.theme,
                        color_discrete_sequence=self.color_scheme, **kwargs)
        else:
            fig = go.Figure(data=[go.Box(y=df[y], name=y,
                                        marker_color=self.color_scheme[0], **kwargs)])
            fig.update_layout(title=title, yaxis_title=y, template=self.theme)
        
        return fig
    
    def create_heatmap(self, df: pd.DataFrame, x: str, y: str, values: str,
                      title: str = "", **kwargs) -> go.Figure:
        """Create a heatmap"""
        pivot_df = df.pivot_table(index=y, columns=x, values=values, aggfunc='mean')
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            colorscale='RdBu',
            **kwargs
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x,
            yaxis_title=y,
            template=self.theme
        )
        
        return fig
    
    def create_area_chart(self, df: pd.DataFrame, x: str, y: Union[str, List[str]],
                         title: str = "", **kwargs) -> go.Figure:
        """Create an area chart"""
        fig = go.Figure()
        
        if isinstance(y, str):
            y = [y]
        
        for i, col in enumerate(y):
            fig.add_trace(go.Scatter(
                x=df[x],
                y=df[col],
                mode='lines',
                name=col,
                fill='tozeroy' if i == 0 else 'tonexty',
                line=dict(color=self.color_scheme[i % len(self.color_scheme)]),
                **kwargs
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x,
            yaxis_title=', '.join(y) if len(y) > 1 else y[0],
            template=self.theme,
            hovermode='x unified'
        )
        
        return fig
    
    def create_violin_plot(self, df: pd.DataFrame, y: str, x: str = None,
                          title: str = "", **kwargs) -> go.Figure:
        """Create a violin plot"""
        if x:
            fig = px.violin(df, x=x, y=y, title=title, template=self.theme,
                           color_discrete_sequence=self.color_scheme, **kwargs)
        else:
            fig = go.Figure(data=[go.Violin(y=df[y], name=y,
                                           marker_color=self.color_scheme[0], **kwargs)])
            fig.update_layout(title=title, yaxis_title=y, template=self.theme)
        
        return fig
    
    def create_sunburst(self, df: pd.DataFrame, path: List[str], values: str,
                       title: str = "", **kwargs) -> go.Figure:
        """Create a sunburst chart"""
        fig = px.sunburst(df, path=path, values=values, title=title,
                         template=self.theme, color_discrete_sequence=self.color_scheme,
                         **kwargs)
        
        return fig
    
    def create_treemap(self, df: pd.DataFrame, path: List[str], values: str,
                      title: str = "", **kwargs) -> go.Figure:
        """Create a treemap"""
        fig = px.treemap(df, path=path, values=values, title=title,
                        template=self.theme, color_discrete_sequence=self.color_scheme,
                        **kwargs)
        
        return fig
    
    def create_waterfall(self, df: pd.DataFrame, x: str, y: str,
                        title: str = "", **kwargs) -> go.Figure:
        """Create a waterfall chart"""
        fig = go.Figure(go.Waterfall(
            x=df[x],
            y=df[y],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            **kwargs
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x,
            yaxis_title=y,
            template=self.theme
        )
        
        return fig
    
    def create_funnel(self, df: pd.DataFrame, x: str, y: str,
                     title: str = "", **kwargs) -> go.Figure:
        """Create a funnel chart"""
        fig = go.Figure(go.Funnel(
            y=df[y],
            x=df[x],
            marker={"color": self.color_scheme},
            **kwargs
        ))
        
        fig.update_layout(title=title, template=self.theme)
        
        return fig
    
    def create_gauge(self, value: float, min_val: float = 0, max_val: float = 100,
                    title: str = "", **kwargs) -> go.Figure:
        """Create a gauge chart"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title},
            gauge={'axis': {'range': [min_val, max_val]},
                   'bar': {'color': self.color_scheme[0]},
                   'steps': [
                       {'range': [min_val, (max_val - min_val) * 0.5 + min_val],
                        'color': "lightgray"},
                       {'range': [(max_val - min_val) * 0.5 + min_val, max_val],
                        'color': "gray"}],
                   'threshold': {'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': value}},
            **kwargs
        ))
        
        fig.update_layout(template=self.theme)
        
        return fig
    
    def create_radar(self, df: pd.DataFrame, r: str, theta: str,
                    title: str = "", **kwargs) -> go.Figure:
        """Create a radar chart"""
        fig = go.Figure(data=go.Scatterpolar(
            r=df[r],
            theta=df[theta],
            fill='toself',
            marker_color=self.color_scheme[0],
            **kwargs
        ))
        
        fig.update_layout(
            title=title,
            polar=dict(
                radialaxis=dict(visible=True, range=[0, df[r].max()])
            ),
            template=self.theme
        )
        
        return fig
    
    def create_sankey(self, source: List[int], target: List[int], value: List[float],
                     labels: List[str], title: str = "", **kwargs) -> go.Figure:
        """Create a sankey diagram"""
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color=self.color_scheme
            ),
            link=dict(
                source=source,
                target=target,
                value=value
            ),
            **kwargs
        )])
        
        fig.update_layout(title=title, template=self.theme)
        
        return fig
    
    def create_candlestick(self, df: pd.DataFrame, date: str, open: str,
                          high: str, low: str, close: str, title: str = "",
                          **kwargs) -> go.Figure:
        """Create a candlestick chart"""
        fig = go.Figure(data=[go.Candlestick(
            x=df[date],
            open=df[open],
            high=df[high],
            low=df[low],
            close=df[close],
            **kwargs
        )])
        
        fig.update_layout(
            title=title,
            xaxis_title=date,
            yaxis_title='Price',
            template=self.theme,
            xaxis_rangeslider_visible=False
        )
        
        return fig
    
    def create_parallel_coordinates(self, df: pd.DataFrame, dimensions: List[str],
                                   color: str = None, title: str = "",
                                   **kwargs) -> go.Figure:
        """Create a parallel coordinates plot"""
        dims = []
        
        for dim in dimensions:
            if pd.api.types.is_numeric_dtype(df[dim]):
                dims.append(dict(
                    range=[df[dim].min(), df[dim].max()],
                    label=dim,
                    values=df[dim]
                ))
            else:
                dims.append(dict(
                    label=dim,
                    values=df[dim].astype('category').cat.codes,
                    tickvals=list(range(len(df[dim].unique()))),
                    ticktext=df[dim].unique()
                ))
        
        if color and pd.api.types.is_numeric_dtype(df[color]):
            line = dict(
                color=df[color],
                colorscale='Viridis',
                showscale=True,
                cmin=df[color].min(),
                cmax=df[color].max()
            )
        else:
            line = dict(color=self.color_scheme[0])
        
        fig = go.Figure(data=go.Parcoords(
            line=line,
            dimensions=dims,
            **kwargs
        ))
        
        fig.update_layout(title=title, template=self.theme)
        
        return fig
    
    def create_3d_scatter(self, df: pd.DataFrame, x: str, y: str, z: str,
                         color: str = None, size: str = None, title: str = "",
                         **kwargs) -> go.Figure:
        """Create a 3D scatter plot"""
        fig = px.scatter_3d(
            df, x=x, y=y, z=z, color=color, size=size,
            title=title, template=self.theme,
            color_discrete_sequence=self.color_scheme,
            **kwargs
        )
        
        return fig
    
    def create_3d_surface(self, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                         title: str = "", **kwargs) -> go.Figure:
        """Create a 3D surface plot"""
        fig = go.Figure(data=[go.Surface(x=x, y=y, z=z, **kwargs)])
        
        fig.update_layout(
            title=title,
            template=self.theme,
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z'
            )
        )
        
        return fig
    
    def create_subplots(self, charts: List[go.Figure], rows: int, cols: int,
                       subplot_titles: List[str] = None, title: str = "",
                       **kwargs) -> go.Figure:
        """Create subplots from multiple charts"""
        fig = make_subplots(
            rows=rows, cols=cols,
            subplot_titles=subplot_titles,
            **kwargs
        )
        
        for i, chart in enumerate(charts):
            row = i // cols + 1
            col = i % cols + 1
            
            for trace in chart.data:
                fig.add_trace(trace, row=row, col=col)
        
        fig.update_layout(title=title, template=self.theme, showlegend=True)
        
        return fig

# Export functions
class DataExporter:
    @staticmethod
    def export_to_csv(df: pd.DataFrame, filename: str = None) -> str:
        """Export dataframe to CSV"""
        if filename is None:
            filename = f"data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        return csv_buffer.getvalue()
    
    @staticmethod
    def export_to_excel(df: pd.DataFrame, filename: str = None) -> bytes:
        """Export dataframe to Excel"""
        if filename is None:
            filename = f"data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Data', index=False)
            
            # Get the xlsxwriter workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['Data']
            
            # Add a format for the header row
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BD',
                'border': 1
            })
            
            # Write the column headers with the defined format
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Set column widths
            for i, col in enumerate(df.columns):
                column_width = max(df[col].astype(str).map(len).max(), len(str(col))) + 2
                worksheet.set_column(i, i, column_width)
        
        excel_buffer.seek(0)
        
        return excel_buffer.getvalue()
    
    @staticmethod
    def export_to_json(df: pd.DataFrame, orient: str = 'records') -> str:
        """Export dataframe to JSON"""
        return df.to_json(orient=orient, date_format='iso')
    
    @staticmethod
    def export_chart_to_html(fig: go.Figure, filename: str = None) -> str:
        """Export Plotly figure to HTML"""
        if filename is None:
            filename = f"chart_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        return fig.to_html(include_plotlyjs='cdn')
    
    @staticmethod
    def export_chart_to_image(fig: go.Figure, format: str = 'png',
                             width: int = 1200, height: int = 800) -> bytes:
        """Export Plotly figure to image (requires kaleido)"""
        return fig.to_image(format=format, width=width, height=height)
    
    @staticmethod
    def create_report(data: Dict[str, Any], charts: List[go.Figure],
                     title: str = "Data Analysis Report") -> str:
        """Create an HTML report with data and charts"""
        html_template = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }}
                h1, h2, h3 {{
                    color: #333;
                }}
                .summary {{
                    background-color: #e8f4f8;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .chart-container {{
                    margin: 30px 0;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #4CAF50;
                    color: white;
                }}
                tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{title}</h1>
                <p>Generated on: {timestamp}</p>
                
                <div class="summary">
                    <h2>Summary</h2>
                    {summary}
                </div>
                
                <h2>Charts</h2>
                {charts}
                
                <h2>Data Details</h2>
                {data_details}
            </div>
        </body>
        </html>
        '''
        
        # Generate summary
        summary_html = '<ul>'
        for key, value in data.get('summary', {}).items():
            summary_html += f'<li><strong>{key}:</strong> {value}</li>'
        summary_html += '</ul>'
        
        # Generate charts HTML
        charts_html = ''
        for i, chart in enumerate(charts):
            chart_html = f'<div class="chart-container" id="chart_{i}"></div>'
            chart_script = f'''
            <script>
                var plotlyData_{i} = {chart.to_json()};
                var data_{i} = JSON.parse(plotlyData_{i}).data;
                var layout_{i} = JSON.parse(plotlyData_{i}).layout;
                Plotly.newPlot('chart_{i}', data_{i}, layout_{i});
            </script>
            '''
            charts_html += chart_html + chart_script
        
        # Generate data details
        data_details_html = ''
        if 'statistics' in data:
            data_details_html += '<h3>Statistics</h3><table>'
            data_details_html += '<tr><th>Column</th><th>Mean</th><th>Median</th><th>Std Dev</th><th>Min</th><th>Max</th></tr>'
            
            for col, stats in data['statistics'].items():
                data_details_html += f'''
                <tr>
                    <td>{col}</td>
                    <td>{stats.get('mean', 'N/A'):.2f}</td>
                    <td>{stats.get('median', 'N/A'):.2f}</td>
                    <td>{stats.get('std', 'N/A'):.2f}</td>
                    <td>{stats.get('min', 'N/A'):.2f}</td>
                    <td>{stats.get('max', 'N/A'):.2f}</td>
                </tr>
                '''
            
            data_details_html += '</table>'
        
        return html_template.format(
            title=title,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            summary=summary_html,
            charts=charts_html,
            data_details=data_details_html
        )

# Advanced analytics functions
class AdvancedAnalytics:
    @staticmethod
    def correlation_analysis(df: pd.DataFrame, method: str = 'pearson') -> pd.DataFrame:
        """Calculate correlation matrix"""
        numeric_df = df.select_dtypes(include=[np.number])
        return numeric_df.corr(method=method)
    
    @staticmethod
    def time_series_decomposition(df: pd.DataFrame, date_col: str,
                                 value_col: str, period: int = None):
        """Perform time series decomposition"""
        from statsmodels.tsa.seasonal import seasonal_decompose
        
        # Ensure date column is datetime
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(date_col)
        df = df.set_index(date_col)
        
        # Perform decomposition
        if period is None:
            # Try to infer period
            if df.index.freq is None:
                df.index.freq = pd.infer_freq(df.index)
            
            if df.index.freq:
                if df.index.freq.startswith('D'):
                    period = 7  # Weekly seasonality
                elif df.index.freq.startswith('M'):
                    period = 12  # Yearly seasonality
                else:
                    period = 4  # Default
        
        decomposition = seasonal_decompose(df[value_col], model='additive', period=period)
        
        return {
            'trend': decomposition.trend,
            'seasonal': decomposition.seasonal,
            'residual': decomposition.resid,
            'observed': decomposition.observed
        }
    
    @staticmethod
    def outlier_detection(df: pd.DataFrame, columns: List[str] = None,
                         method: str = 'iqr', threshold: float = 1.5) -> pd.DataFrame:
        """Detect outliers in data"""
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        outliers = pd.DataFrame(index=df.index)
        
        for col in columns:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                if method == 'iqr':
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    outliers[f'{col}_outlier'] = (
                        (df[col] < Q1 - threshold * IQR) |
                        (df[col] > Q3 + threshold * IQR)
                    )
                elif method == 'zscore':
                    z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                    outliers[f'{col}_outlier'] = z_scores > threshold
        
        return outliers
    
    @staticmethod
    def feature_importance(X: pd.DataFrame, y: pd.Series,
                          method: str = 'random_forest') -> pd.DataFrame:
        """Calculate feature importance"""
        from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
        from sklearn.preprocessing import LabelEncoder
        
        # Prepare data
        X_encoded = X.copy()
        
        # Encode categorical variables
        for col in X_encoded.columns:
            if X_encoded[col].dtype == 'object':
                le = LabelEncoder()
                X_encoded[col] = le.fit_transform(X_encoded[col].fillna('missing'))
        
        # Determine if regression or classification
        if y.dtype == 'object' or y.nunique() < 20:
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            if y.dtype == 'object':
                le = LabelEncoder()
                y = le.fit_transform(y)
        else:
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        # Fit model
        model.fit(X_encoded, y)
        
        # Get feature importance
        importance_df = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return importance_df
    
    @staticmethod
    def clustering_analysis(df: pd.DataFrame, n_clusters: int = 3,
                           features: List[str] = None) -> Dict[str, Any]:
        """Perform clustering analysis"""
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        
        # Select features
        if features is None:
            features = df.select_dtypes(include=[np.number]).columns.tolist()
        
        X = df[features].copy()
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X_scaled)
        
        # Calculate metrics
        from sklearn.metrics import silhouette_score
        silhouette = silhouette_score(X_scaled, clusters)
        
        return {
            'clusters': clusters,
            'centroids': scaler.inverse_transform(kmeans.cluster_centers_),
            'silhouette_score': silhouette,
            'features': features
        }
    
    @staticmethod
    def regression_analysis(df: pd.DataFrame, target: str,
                           features: List[str] = None) -> Dict[str, Any]:
        """Perform regression analysis"""
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import r2_score, mean_squared_error
        from sklearn.model_selection import train_test_split
        
        # Prepare data
        if features is None:
            features = [col for col in df.select_dtypes(include=[np.number]).columns
                       if col != target]
        
        X = df[features].copy()
        y = df[target].copy()
        
        # Handle missing values
        mask = X.notna().all(axis=1) & y.notna()
        X = X[mask]
        y = y[mask]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Fit model
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        # Calculate metrics
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)
        train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
        test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
        
        # Create coefficient dataframe
        coef_df = pd.DataFrame({
            'feature': features,
            'coefficient': model.coef_
        }).sort_values('coefficient', key=abs, ascending=False)
        
        return {
            'model': model,
            'coefficients': coef_df,
            'intercept': model.intercept_,
            'train_r2': train_r2,
            'test_r2': test_r2,
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'predictions': {
                'train': y_pred_train,
                'test': y_pred_test
            }
        }

# Streamlit UI components
class UIComponents:
    @staticmethod
    def render_header():
        """Render application header"""
        st.set_page_config(
            page_title="Advanced Data Visualization Platform",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        st.markdown("""
        <style>
        .main {
            padding-top: 2rem;
        }
        .stApp {
            background-color: #f5f5f5;
        }
        .css-1d391kg {
            padding-top: 3.5rem;
        }
        .metric-card {
            background-color: white;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
        .chart-container {
            background-color: white;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Header
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.title("📊 Advanced Data Visualization Platform")
            st.caption(f"Version {APP_VERSION} | Powerful analytics and visualization tools")
    
    @staticmethod
    def render_sidebar():
        """Render sidebar navigation"""
        with st.sidebar:
            st.image("https://via.placeholder.com/300x100?text=DataViz+Pro", width=300)
            
            st.markdown("---")
            
            # Navigation
            st.subheader("Navigation")
            page = st.radio(
                "Select Page",
                ["🏠 Home", "📁 Data Management", "📈 Visualizations",
                 "📊 Dashboard", "🔬 Analytics", "⚙️ Settings"]
            )
            
            st.markdown("---")
            
            # Quick stats
            if 'data_sources' in st.session_state:
                st.subheader("Quick Stats")
                st.metric("Data Sources", len(st.session_state.data_sources))
                st.metric("Active Charts", len(st.session_state.get('charts', [])))
                st.metric("Dashboards", len(st.session_state.get('dashboards', [])))
            
            st.markdown("---")
            
            # Help section
            with st.expander("ℹ️ Help & Support"):
                st.markdown("""
                - **Documentation**: [View Docs](#)
                - **Tutorials**: [Watch Videos](#)
                - **Support**: support@dataviz.com
                - **Version**: {APP_VERSION}
                """)
            
            return page
    
    @staticmethod
    def render_data_upload():
        """Render data upload interface"""
        st.header("📁 Data Upload")
        
        upload_method = st.radio(
            "Select upload method",
            ["File Upload", "Database Connection", "API Connection", "Sample Data"]
        )
        
        if upload_method == "File Upload":
            uploaded_file = st.file_uploader(
                "Choose a file",
                type=SUPPORTED_FILE_TYPES,
                help=f"Supported formats: {', '.join(SUPPORTED_FILE_TYPES)}"
            )
            
            if uploaded_file is not None:
                # File info
                file_details = {
                    "Filename": uploaded_file.name,
                    "File Size": f"{uploaded_file.size / 1024:.2f} KB",
                    "File Type": Path(uploaded_file.name).suffix
                }
                
                col1, col2 = st.columns(2)
                with col1:
                    st.json(file_details)
                
                # Process file
                if st.button("Process File", type="primary"):
                    with st.spinner("Processing file..."):
                        try:
                            # Save uploaded file
                            temp_path = Path(tempfile.gettempdir()) / uploaded_file.name
                            with open(temp_path, 'wb') as f:
                                f.write(uploaded_file.getbuffer())
                            
                            # Load data
                            processor = DataProcessor()
                            df = processor.load_file(str(temp_path))
                            
                            # Detect data types
                            data_types = processor.detect_data_types(df)
                            
                            # Create data source
                            data_source = DataSource(
                                id=str(uuid.uuid4()),
                                name=uploaded_file.name,
                                type='file',
                                path=str(temp_path),
                                columns=df.columns.tolist(),
                            row_count=len(df),
                            created_at=datetime.now(),
                            updated_at=datetime.now(),
                            metadata={'source': 'sample'}
                        )
                        
                        # Save to session state
                        if 'data_sources' not in st.session_state:
                            st.session_state.data_sources = {}
                        
                        st.session_state.data_sources[data_source.id] = data_source
                        st.session_state[f'df_{data_source.id}'] = df
                        
                        st.success(f"Successfully loaded {selected_dataset}")
                        st.dataframe(df.head())
                        
                    except Exception as e:
                        st.error(f"Error loading sample data: {str(e)}")
    
    @staticmethod
    def render_visualization_builder():
        """Render visualization builder interface"""
        st.header("📈 Visualization Builder")
        
        if 'data_sources' not in st.session_state or not st.session_state.data_sources:
            st.warning("No data sources available. Please upload data first.")
            return
        
        # Select data source
        data_source_names = {ds.id: ds.name for ds in st.session_state.data_sources.values()}
        selected_source_id = st.selectbox(
            "Select Data Source",
            options=list(data_source_names.keys()),
            format_func=lambda x: data_source_names[x]
        )
        
        if selected_source_id:
            df = st.session_state[f'df_{selected_source_id}']
            
            # Chart type selection
            col1, col2 = st.columns([1, 2])
            
            with col1:
                chart_type = st.selectbox(
                    "Chart Type",
                    options=[ct.value for ct in ChartType]
                )
                
                # Get numeric and categorical columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                all_cols = df.columns.tolist()
                
                # Chart-specific inputs
                chart_config = {}
                
                if chart_type == ChartType.LINE.value:
                    chart_config['x'] = st.selectbox("X-axis", all_cols)
                    chart_config['y'] = st.multiselect("Y-axis", numeric_cols)
                    chart_config['color'] = st.selectbox("Color by", ['None'] + categorical_cols)
                
                elif chart_type == ChartType.BAR.value:
                    chart_config['x'] = st.selectbox("X-axis", all_cols)
                    chart_config['y'] = st.multiselect("Y-axis", numeric_cols)
                    chart_config['orientation'] = st.radio("Orientation", ['Vertical', 'Horizontal'])
                    chart_config['barmode'] = st.radio("Bar Mode", ['group', 'stack', 'relative'])
                
                elif chart_type == ChartType.SCATTER.value:
                    chart_config['x'] = st.selectbox("X-axis", numeric_cols)
                    chart_config['y'] = st.selectbox("Y-axis", numeric_cols)
                    chart_config['size'] = st.selectbox("Size", ['None'] + numeric_cols)
                    chart_config['color'] = st.selectbox("Color", ['None'] + all_cols)
                
                elif chart_type == ChartType.PIE.value:
                    chart_config['values'] = st.selectbox("Values", numeric_cols)
                    chart_config['names'] = st.selectbox("Names", categorical_cols)
                
                elif chart_type == ChartType.HISTOGRAM.value:
                    chart_config['x'] = st.selectbox("Column", numeric_cols)
                    chart_config['bins'] = st.slider("Number of bins", 10, 100, 30)
                
                elif chart_type == ChartType.BOX.value:
                    chart_config['y'] = st.selectbox("Y-axis", numeric_cols)
                    chart_config['x'] = st.selectbox("Group by", ['None'] + categorical_cols)
                
                elif chart_type == ChartType.HEATMAP.value:
                    chart_config['x'] = st.selectbox("X-axis", categorical_cols)
                    chart_config['y'] = st.selectbox("Y-axis", categorical_cols)
                    chart_config['values'] = st.selectbox("Values", numeric_cols)
                
                # Common options
                st.subheader("Chart Options")
                chart_config['title'] = st.text_input("Chart Title", value=f"{chart_type} Chart")
                chart_config['height'] = st.slider("Height", 400, 1000, 600)
                
                # Color scheme
                chart_config['color_scheme'] = st.selectbox(
                    "Color Scheme",
                    list(COLOR_SCHEMES.keys())
                )
                
                # Filters
                st.subheader("Filters")
                filters = []
                
                if st.checkbox("Add filters"):
                    num_filters = st.number_input("Number of filters", 1, 5, 1)
                    
                    for i in range(num_filters):
                        with st.expander(f"Filter {i+1}"):
                            filter_col = st.selectbox(f"Column {i}", all_cols, key=f"filter_col_{i}")
                            filter_op = st.selectbox(
                                f"Operator {i}",
                                [op.value for op in FilterOperator],
                                key=f"filter_op_{i}"
                            )
                            
                            # Dynamic value input based on operator
                            if filter_op in ['equals', 'not equals', 'contains', 'not contains',
                                           'starts with', 'ends with']:
                                filter_val = st.text_input(f"Value {i}", key=f"filter_val_{i}")
                            elif filter_op in ['greater than', 'less than', 'greater or equal',
                                             'less or equal']:
                                filter_val = st.number_input(f"Value {i}", key=f"filter_val_{i}")
                            elif filter_op == 'between':
                                col1, col2 = st.columns(2)
                                with col1:
                                    min_val = st.number_input(f"Min {i}", key=f"filter_min_{i}")
                                with col2:
                                    max_val = st.number_input(f"Max {i}", key=f"filter_max_{i}")
                                filter_val = [min_val, max_val]
                            elif filter_op in ['in', 'not in']:
                                filter_val = st.multiselect(
                                    f"Values {i}",
                                    df[filter_col].unique(),
                                    key=f"filter_vals_{i}"
                                )
                            else:
                                filter_val = None
                            
                            if filter_val is not None:
                                filters.append({
                                    'column': filter_col,
                                    'operator': filter_op,
                                    'value': filter_val
                                })
            
            with col2:
                # Preview button
                if st.button("Generate Chart", type="primary"):
                    try:
                        # Apply filters
                        df_filtered = df.copy()
                        if filters:
                            processor = DataProcessor()
                            df_filtered = processor.filter_data(df_filtered, filters)
                        
                        # Create chart
                        chart_builder = ChartBuilder()
                        chart_builder.set_color_scheme(chart_config.get('color_scheme', 'default'))
                        
                        fig = None
                        
                        if chart_type == ChartType.LINE.value and chart_config.get('y'):
                            fig = chart_builder.create_line_chart(
                                df_filtered,
                                x=chart_config['x'],
                                y=chart_config['y'],
                                title=chart_config['title']
                            )
                        
                        elif chart_type == ChartType.BAR.value and chart_config.get('y'):
                            fig = chart_builder.create_bar_chart(
                                df_filtered,
                                x=chart_config['x'],
                                y=chart_config['y'],
                                title=chart_config['title'],
                                orientation='v' if chart_config['orientation'] == 'Vertical' else 'h',
                                barmode=chart_config['barmode']
                            )
                        
                        elif chart_type == ChartType.SCATTER.value:
                            size = chart_config['size'] if chart_config['size'] != 'None' else None
                            color = chart_config['color'] if chart_config['color'] != 'None' else None
                            
                            fig = chart_builder.create_scatter_plot(
                                df_filtered,
                                x=chart_config['x'],
                                y=chart_config['y'],
                                size=size,
                                color=color,
                                title=chart_config['title']
                            )
                        
                        elif chart_type == ChartType.PIE.value:
                            fig = chart_builder.create_pie_chart(
                                df_filtered,
                                values=chart_config['values'],
                                names=chart_config['names'],
                                title=chart_config['title']
                            )
                        
                        elif chart_type == ChartType.HISTOGRAM.value:
                            fig = chart_builder.create_histogram(
                                df_filtered,
                                x=chart_config['x'],
                                nbins=chart_config['bins'],
                                title=chart_config['title']
                            )
                        
                        elif chart_type == ChartType.BOX.value:
                            x = chart_config['x'] if chart_config['x'] != 'None' else None
                            
                            fig = chart_builder.create_box_plot(
                                df_filtered,
                                y=chart_config['y'],
                                x=x,
                                title=chart_config['title']
                            )
                        
                        elif chart_type == ChartType.HEATMAP.value:
                            fig = chart_builder.create_heatmap(
                                df_filtered,
                                x=chart_config['x'],
                                y=chart_config['y'],
                                values=chart_config['values'],
                                title=chart_config['title']
                            )
                        
                        if fig:
                            fig.update_layout(height=chart_config['height'])
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Save chart option
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                if st.button("💾 Save Chart"):
                                    chart = Chart(
                                        id=str(uuid.uuid4()),
                                        name=chart_config['title'],
                                        type=ChartType(chart_type),
                                        data_source_id=selected_source_id,
                                        config=chart_config,
                                        created_at=datetime.now(),
                                        updated_at=datetime.now()
                                    )
                                    
                                    if 'charts' not in st.session_state:
                                        st.session_state.charts = {}
                                    
                                    st.session_state.charts[chart.id] = chart
                                    st.success("Chart saved successfully!")
                            
                            with col2:
                                # Export options
                                export_format = st.selectbox("Export as", ["HTML", "PNG", "PDF"])
                                
                            with col3:
                                if st.button("📥 Export"):
                                    exporter = DataExporter()
                                    
                                    if export_format == "HTML":
                                        html = exporter.export_chart_to_html(fig)
                                        st.download_button(
                                            "Download HTML",
                                            html,
                                            f"{chart_config['title']}.html",
                                            "text/html"
                                        )
                        
                    except Exception as e:
                        st.error(f"Error creating chart: {str(e)}")
    
    @staticmethod
    def render_dashboard():
        """Render dashboard interface"""
        st.header("📊 Dashboard")
        
        tab1, tab2, tab3 = st.tabs(["View Dashboards", "Create Dashboard", "Manage Dashboards"])
        
        with tab1:
            if 'dashboards' not in st.session_state or not st.session_state.dashboards:
                st.info("No dashboards created yet. Create your first dashboard in the 'Create Dashboard' tab.")
            else:
                # Select dashboard
                dashboard_names = {d.id: d.name for d in st.session_state.dashboards.values()}
                selected_dashboard_id = st.selectbox(
                    "Select Dashboard",
                    options=list(dashboard_names.keys()),
                    format_func=lambda x: dashboard_names[x]
                )
                
                if selected_dashboard_id:
                    dashboard = st.session_state.dashboards[selected_dashboard_id]
                    
                    # Render dashboard
                    st.subheader(dashboard.name)
                    
                    # Apply global filters
                    if dashboard.filters:
                        st.sidebar.subheader("Dashboard Filters")
                        # Implement global filters here
                    
                    # Render charts in grid
                    if dashboard.charts:
                        cols = dashboard.layout.get('columns', 2)
                        rows = (len(dashboard.charts) + cols - 1) // cols
                        
                        for row in range(rows):
                            columns = st.columns(cols)
                            for col in range(cols):
                                chart_idx = row * cols + col
                                if chart_idx < len(dashboard.charts):
                                    chart_id = dashboard.charts[chart_idx]
                                    if chart_id in st.session_state.get('charts', {}):
                                        chart = st.session_state.charts[chart_id]
                                        
                                        with columns[col]:
                                            # Recreate and display chart
                                            # This would need the actual chart recreation logic
                                            st.info(f"Chart: {chart.name}")
        
        with tab2:
            st.subheader("Create New Dashboard")
            
            dashboard_name = st.text_input("Dashboard Name")
            dashboard_description = st.text_area("Description")
            
            # Layout options
            col1, col2 = st.columns(2)
            
            with col1:
                layout_columns = st.number_input("Number of columns", 1, 4, 2)
            
            with col2:
                layout_spacing = st.slider("Spacing", 0, 50, 10)
            
            # Select charts
            if 'charts' in st.session_state and st.session_state.charts:
                available_charts = {c.id: c.name for c in st.session_state.charts.values()}
                selected_charts = st.multiselect(
                    "Select charts to include",
                    options=list(available_charts.keys()),
                    format_func=lambda x: available_charts[x]
                )
                
                if selected_charts:
                    # Preview layout
                    st.subheader("Layout Preview")
                    
                    cols = layout_columns
                    rows = (len(selected_charts) + cols - 1) // cols
                    
                    for row in range(rows):
                        columns = st.columns(cols)
                        for col in range(cols):
                            chart_idx = row * cols + col
                            if chart_idx < len(selected_charts):
                                with columns[col]:
                                    st.info(f"📊 {available_charts[selected_charts[chart_idx]]}")
                    
                    # Create dashboard button
                    if st.button("Create Dashboard", type="primary"):
                        if dashboard_name:
                            dashboard = Dashboard(
                                id=str(uuid.uuid4()),
                                name=dashboard_name,
                                charts=selected_charts,
                                layout={
                                    'columns': layout_columns,
                                    'spacing': layout_spacing
                                },
                                filters=[],
                                created_at=datetime.now(),
                                updated_at=datetime.now(),
                                metadata={'description': dashboard_description}
                            )
                            
                            if 'dashboards' not in st.session_state:
                                st.session_state.dashboards = {}
                            
                            st.session_state.dashboards[dashboard.id] = dashboard
                            st.success("Dashboard created successfully!")
                        else:
                            st.error("Please enter a dashboard name")
            else:
                st.warning("No charts available. Create some charts first in the Visualizations section.")
        
        with tab3:
            st.subheader("Manage Dashboards")
            
            if 'dashboards' in st.session_state and st.session_state.dashboards:
                # List dashboards
                for dashboard_id, dashboard in st.session_state.dashboards.items():
                    with st.expander(f"📊 {dashboard.name}"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write(f"**Created:** {dashboard.created_at.strftime('%Y-%m-%d %H:%M')}")
                            st.write(f"**Charts:** {len(dashboard.charts)}")
                        
                        with col2:
                            if st.button(f"Edit", key=f"edit_{dashboard_id}"):
                                st.info("Edit functionality would go here")
                        
                        with col3:
                            if st.button(f"Delete", key=f"delete_{dashboard_id}"):
                                del st.session_state.dashboards[dashboard_id]
                                st.rerun()
            else:
                st.info("No dashboards created yet.")
    
    @staticmethod
    def render_analytics():
        """Render analytics interface"""
        st.header("🔬 Advanced Analytics")
        
        if 'data_sources' not in st.session_state or not st.session_state.data_sources:
            st.warning("No data sources available. Please upload data first.")
            return
        
        # Select data source
        data_source_names = {ds.id: ds.name for ds in st.session_state.data_sources.values()}
        selected_source_id = st.selectbox(
            "Select Data Source",
            options=list(data_source_names.keys()),
            format_func=lambda x: data_source_names[x]
        )
        
        if selected_source_id:
            df = st.session_state[f'df_{selected_source_id}']
            
            # Analytics tabs
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 Statistics", "🔗 Correlations", "📈 Time Series",
                "🎯 Clustering", "📉 Regression"
            ])
            
            with tab1:
                st.subheader("Descriptive Statistics")
                
                # Select columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                selected_cols = st.multiselect(
                    "Select columns for analysis",
                    numeric_cols,
                    default=numeric_cols[:5] if len(numeric_cols) > 5 else numeric_cols
                )
                
                if selected_cols:
                    # Calculate statistics
                    processor = DataProcessor()
                    stats = processor.calculate_statistics(df, selected_cols)
                    
                    # Display statistics
                    stats_df = pd.DataFrame(stats).T
                    st.dataframe(stats_df.style.format("{:.2f}"))
                    
                    # Visualize distributions
                    st.subheader("Distribution Plots")
                    
                    cols_per_row = 3
                    rows = (len(selected_cols) + cols_per_row - 1) // cols_per_row
                    
                    chart_builder = ChartBuilder()
                    
                    for row in range(rows):
                        columns = st.columns(cols_per_row)
                        for col in range(cols_per_row):
                            idx = row * cols_per_row + col
                            if idx < len(selected_cols):
                                with columns[col]:
                                    fig = chart_builder.create_histogram(
                                        df, selected_cols[idx],
                                        title=f"Distribution of {selected_cols[idx]}"
                                    )
                                    fig.update_layout(height=300)
                                    st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                st.subheader("Correlation Analysis")
                
                # Correlation method
                corr_method = st.selectbox(
                    "Correlation method",
                    ['pearson', 'spearman', 'kendall']
                )
                
                # Calculate correlations
                analytics = AdvancedAnalytics()
                corr_matrix = analytics.correlation_analysis(df, method=corr_method)
                
                # Display heatmap
                if not corr_matrix.empty:
                    fig = go.Figure(data=go.Heatmap(
                        z=corr_matrix.values,
                        x=corr_matrix.columns,
                        y=corr_matrix.columns,
                        colorscale='RdBu',
                        zmid=0,
                        text=corr_matrix.values.round(2),
                        texttemplate='%{text}',
                        textfont={"size": 10}
                    ))
                    
                    fig.update_layout(
                        title=f"{corr_method.capitalize()} Correlation Matrix",
                        height=600
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Top correlations
                    st.subheader("Top Correlations")
                    
                    # Get upper triangle of correlation matrix
                    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
                    corr_list = []
                    
                    for i in range(len(corr_matrix.columns)):
                        for j in range(i+1, len(corr_matrix.columns)):
                            if mask[i, j]:
                                corr_list.append({
                                    'Variable 1': corr_matrix.columns[i],
                                    'Variable 2': corr_matrix.columns[j],
                                    'Correlation': corr_matrix.iloc[i, j]
                                })
                    
                    corr_df = pd.DataFrame(corr_list)
                    corr_df = corr_df.sort_values('Correlation', key=abs, ascending=False).head(20)
                    
                    st.dataframe(corr_df.style.format({'Correlation': '{:.3f}'}))
            
            with tab3:
                st.subheader("Time Series Analysis")
                
                # Check for datetime columns
                date_cols = []
                for col in df.columns:
                    if pd.api.types.is_datetime64_any_dtype(df[col]):
                        date_cols.append(col)
                    else:
                        # Try to convert to datetime
                        try:
                            pd.to_datetime(df[col], errors='coerce')
                            date_cols.append(col)
                        except:
                            pass
                
                if date_cols:
                    date_col = st.selectbox("Select date column", date_cols)
                    value_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                    value_col = st.selectbox("Select value column", value_cols)
                    
                    if st.button("Perform Time Series Decomposition"):
                        try:
                            analytics = AdvancedAnalytics()
                            decomposition = analytics.time_series_decomposition(
                                df, date_col, value_col
                            )
                            
                            # Plot components
                            fig = make_subplots(
                                rows=4, cols=1,
                                subplot_titles=('Observed', 'Trend', 'Seasonal', 'Residual'),
                                shared_xaxes=True
                            )
                            
                            fig.add_trace(
                                go.Scatter(x=decomposition['observed'].index,
                                         y=decomposition['observed'], name='Observed'),
                                row=1, col=1
                            )
                            
                            fig.add_trace(
                                go.Scatter(x=decomposition['trend'].index,
                                         y=decomposition['trend'], name='Trend'),
                                row=2, col=1
                            )
                            
                            fig.add_trace(
                                go.Scatter(x=decomposition['seasonal'].index,
                                         y=decomposition['seasonal'], name='Seasonal'),
                                row=3, col=1
                            )
                            
                            fig.add_trace(
                                go.Scatter(x=decomposition['residual'].index,
                                         y=decomposition['residual'], name='Residual'),
                                row=4, col=1
                            )
                            
                            fig.update_layout(height=800, title="Time Series Decomposition")
                            st.plotly_chart(fig, use_container_width=True)
                            
                        except Exception as e:
                            st.error(f"Error in time series analysis: {str(e)}")
                else:
                    st.warning("No datetime columns found in the dataset.")
            
            with tab4:
                st.subheader("Clustering Analysis")
                
                # Select features
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                selected_features = st.multiselect(
                    "Select features for clustering",
                    numeric_cols,
                    default=numeric_cols[:3] if len(numeric_cols) > 3 else numeric_cols
                )
                
                if len(selected_features) >= 2:
                    n_clusters = st.slider("Number of clusters", 2, 10, 3)
                    
                    if st.button("Perform Clustering"):
                        analytics = AdvancedAnalytics()
                        clustering_results = analytics.clustering_analysis(
                            df, n_clusters=n_clusters, features=selected_features
                        )
                        
                        # Add clusters to dataframe
                        df_clustered = df.copy()
                        df_clustered['Cluster'] = clustering_results['clusters']
                        
                        # Display results
                        st.metric("Silhouette Score",
                                f"{clustering_results['silhouette_score']:.3f}")
                        
                        # Visualize clusters
                        if len(selected_features) == 2:
                            fig = px.scatter(
                                df_clustered,
                                x=selected_features[0],
                                y=selected_features[1],
                                color='Cluster',
                                title="Clustering Results"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        elif len(selected_features) >= 3:
                            fig = px.scatter_3d(
                                df_clustered,
                                x=selected_features[0],
                                y=selected_features[1],
                                z=selected_features[2],
                                color='Cluster',
                                title="Clustering Results (3D)"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Cluster statistics
                        st.subheader("Cluster Statistics")
                        cluster_stats = df_clustered.groupby('Cluster')[selected_features].agg(['mean', 'std'])
                        st.dataframe(cluster_stats)
                else:
                    st.warning("Please select at least 2 features for clustering.")
            
            with tab5:
                st.subheader("Regression Analysis")
                
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                
                if len(numeric_cols) >= 2:
                    target = st.selectbox("Select target variable", numeric_cols)
                    features = st.multiselect(
                        "Select feature variables",
                        [col for col in numeric_cols if col != target]
                    )
                    
                    if features and st.button("Perform Regression"):
                        analytics = AdvancedAnalytics()
                        regression_results = analytics.regression_analysis(
                            df, target=target, features=features
                        )
                        
                        # Display metrics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Train R²",
                                    f"{regression_results['train_r2']:.3f}")
                        with col2:
                            st.metric("Test R²",
                                    f"{regression_results['test_r2']:.3f}")
                        with col3:
                            st.metric("Train RMSE",
                                    f"{regression_results['train_rmse']:.2f}")
                        with col4:
                            st.metric("Test RMSE",
                                    f"{regression_results['test_rmse']:.2f}")
                        
                        # Coefficients
                        st.subheader("Feature Coefficients")
                        coef_df = regression_results['coefficients']
                        
                        fig = px.bar(
                            coef_df,
                            x='coefficient',
                            y='feature',
                            orientation='h',
                            title="Feature Importance"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Predictions vs Actual
                        st.subheader("Predictions vs Actual")
                        
                        # This would need the actual y_test values from the regression
                        st.info("Prediction plot would be displayed here")
                else:
                    st.warning("Not enough numeric columns for regression analysis.")

# Main application
def main():
    # Initialize session state
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.data_sources = {}
        st.session_state.charts = {}
        st.session_state.dashboards = {}
        st.session_state.current_user = None
        
        # Initialize database
        db_manager = DatabaseManager()
    
    # Render UI components
    ui = UIComponents()
    ui.render_header()
    
    # Get selected page
    page = ui.render_sidebar()
    
    # Route to appropriate page
    if page == "🏠 Home":
        st.header("Welcome to DataViz Pro")
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Data Sources",
                len(st.session_state.data_sources),
                "+2 from last week"
            )
        
        with col2:
            st.metric(
                "Total Charts",
                len(st.session_state.get('charts', [])),
                "+5 from last week"
            )
        
        with col3:
            st.metric(
                "Dashboards",
                len(st.session_state.get('dashboards', [])),
                "+1 from last week"
            )
        
        with col4:
            total_rows = sum(
                len(st.session_state.get(f'df_{ds_id}', pd.DataFrame()))
                for ds_id in st.session_state.data_sources
            )
            st.metric(
                "Total Rows",
                f"{total_rows:,}",
                "+10K from last week"
            )
        
        # Recent activity
        st.subheader("Recent Activity")
        
        activities = [
            {"time": "2 hours ago", "action": "Created dashboard", "object": "Sales Overview"},
            {"time": "5 hours ago", "action": "Uploaded file", "object": "Q4_data.csv"},
            {"time": "1 day ago", "action": "Created chart", "object": "Revenue Trend"},
            {"time": "2 days ago", "action": "Shared dashboard", "object": "KPI Dashboard"},
        ]
        
        for activity in activities:
            st.write(f"⏰ {activity['time']}: {activity['action']} - **{activity['object']}**")
        
        # Quick actions
        st.subheader("Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📁 Upload Data", use_container_width=True):
                st.session_state.page = "📁 Data Management"
                st.rerun()
        
        with col2:
            if st.button("📈 Create Chart", use_container_width=True):
                st.session_state.page = "📈 Visualizations"
                st.rerun()
        
        with col3:
            if st.button("📊 View Dashboards", use_container_width=True):
                st.session_state.page = "📊 Dashboard"
                st.rerun()
    
    elif page == "📁 Data Management":
        ui.render_data_upload()
        
        # Data sources list
        if st.session_state.data_sources:
            st.header("📋 Data Sources")
            
            for ds_id, data_source in st.session_state.data_sources.items():
                with st.expander(f"📁 {data_source.name}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Type:** {data_source.type}")
                        st.write(f"**Rows:** {data_source.row_count:,}")
                        st.write(f"**Columns:** {len(data_source.columns)}")
                    
                    with col2:
                        st.write(f"**Created:** {data_source.created_at.strftime('%Y-%m-%d %H:%M')}")
                        st.write(f"**Updated:** {data_source.updated_at.strftime('%Y-%m-%d %H:%M')}")
                    
                    with col3:
                        if st.button(f"View Data", key=f"view_{ds_id}"):
                            df = st.session_state[f'df_{ds_id}']
                            st.dataframe(df.head(100))
                        
                        if st.button(f"Delete", key=f"delete_{ds_id}"):
                            del st.session_state.data_sources[ds_id]
                            del st.session_state[f'df_{ds_id}']
                            st.rerun()
    
    elif page == "📈 Visualizations":
        ui.render_visualization_builder()
    
    elif page == "📊 Dashboard":
        ui.render_dashboard()
    
    elif page == "🔬 Analytics":
        ui.render_analytics()
    
    elif page == "⚙️ Settings":
        st.header("⚙️ Settings")
        
        tab1, tab2, tab3 = st.tabs(["General", "Export Options", "About"])
        
        with tab1:
            st.subheader("General Settings")
            
            # Theme
            theme = st.selectbox("Application Theme", ["Light", "Dark", "Auto"])
            
            # Default color scheme
            default_colors = st.selectbox(
                "Default Color Scheme",
                list(COLOR_SCHEMES.keys())
            )
            
            # Data settings
            st.subheader("Data Settings")
            
            auto_detect_types = st.checkbox("Auto-detect data types", value=True)
            remove_duplicates = st.checkbox("Remove duplicates by default", value=True)
            
            # Performance settings
            st.subheader("Performance Settings")
            
            cache_enabled = st.checkbox("Enable caching", value=True)
            cache_ttl = st.number_input("Cache TTL (seconds)", 60, 3600, 3600)
            
            if st.button("Save Settings"):
                st.success("Settings saved successfully!")
        
        with tab2:
            st.subheader("Export Options")
            
            # Chart export settings
            st.write("**Chart Export Defaults**")
            
            chart_width = st.number_input("Default width (px)", 800, 2000, 1200)
            chart_height = st.number_input("Default height (px)", 400, 1500, 800)
            chart_format = st.selectbox("Default format", ["PNG", "SVG", "PDF", "HTML"])
            
            # Data export settings
            st.write("**Data Export Defaults**")
            
            include_index = st.checkbox("Include index in exports", value=False)
            date_format = st.text_input("Date format", "%Y-%m-%d")
            
        with tab3:
            st.subheader("About DataViz Pro")
            
            st.write(f"""
            **Version:** {APP_VERSION}
            
            **Features:**
            - 📁 Multiple data source support
            - 📊 20+ chart types
            - 🎨 Customizable visualizations
            - 📈 Advanced analytics
            - 📱 Responsive design
            - 🔒 Secure data handling
            
            **Support:**
            - Email: support@dataviz.com
            - Documentation: docs.dataviz.com
            - Community: community.dataviz.com
            
            **License:** Enterprise License
            """)
            
            # System info
            with st.expander("System Information"):
                st.json({
                    "Python Version": sys.version.split()[0],
                    "Streamlit Version": st.__version__,
                    "Pandas Version": pd.__version__,
                    "Plotly Version": "5.x",
                    "NumPy Version": np.__version__
                })

if __name__ == "__main__":
    main()list(),
                                row_count=len(df),
                                created_at=datetime.now(),
                                updated_at=datetime.now(),
                                metadata={'data_types': data_types}
                            )
                            
                            # Save to session state
                            if 'data_sources' not in st.session_state:
                                st.session_state.data_sources = {}
                            
                            st.session_state.data_sources[data_source.id] = data_source
                            st.session_state[f'df_{data_source.id}'] = df
                            
                            st.success(f"Successfully loaded {len(df):,} rows and {len(df.columns)} columns")
                            
                            # Show preview
                            st.subheader("Data Preview")
                            st.dataframe(df.head(100))
                            
                            # Show data info
                            with st.expander("Data Information"):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.write("**Column Types:**")
                                    for col, dtype in data_types.items():
                                        st.write(f"- {col}: {dtype}")
                                
                                with col2:
                                    st.write("**Basic Statistics:**")
                                    st.write(df.describe())
                            
                            # Clean temp file
                            temp_path.unlink()
                            
                        except Exception as e:
                            st.error(f"Error processing file: {str(e)}")
        
        elif upload_method == "Sample Data":
            st.subheader("Load Sample Data")
            
            sample_datasets = {
                "Sales Data": "https://raw.githubusercontent.com/plotly/datasets/master/sales_data_sample.csv",
                "Iris Dataset": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv",
                "Titanic Dataset": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv",
                "Stock Prices": "https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv"
            }
            
            selected_dataset = st.selectbox("Select sample dataset", list(sample_datasets.keys()))
            
            if st.button("Load Sample Data", type="primary"):
                with st.spinner("Loading sample data..."):
                    try:
                        df = pd.read_csv(sample_datasets[selected_dataset])
                        
                        # Create data source
                        data_source = DataSource(
                            id=str(uuid.uuid4()),
                            name=selected_dataset,
                            type='sample',
                            path=sample_datasets[selected_dataset],
                            columns=df.columns.to
