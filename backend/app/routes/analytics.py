"""
Analytics Routes for Local Producer Web Application

This module provides analytics tracking endpoints, business intelligence,
and reporting APIs with Romanian marketplace optimization.
"""

import logging
import json
from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify, Response
from typing import Dict, List, Any
from app.models.analytics import (
    AnalyticsEvent, EcommerceEvent, PerformanceMetric, 
    UserJourneyStep, BusinessKPI, analytics_repo
)
from app.utils.error_handlers import (
    success_response, create_error_response, ValidationError
)
from app.utils.auth_middleware import require_admin_auth

# Create analytics blueprint
analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/events', methods=['POST'])
def store_analytics_events():
    """
    Store batch of analytics events.
    
    Accepts batch of analytics events from frontend and stores them
    for business intelligence and performance monitoring.
    """
    try:
        data = request.get_json()
        if not data or 'events' not in data:
            response, status = create_error_response(
                "ANALYTICS_001",
                "Events data is required",
                400
            )
            return jsonify(response), status
        
        events_data = data['events']
        batch_info = data.get('batch_info', {})
        
        # Validate events
        if not isinstance(events_data, list) or len(events_data) == 0:
            response, status = create_error_response(
                "ANALYTICS_002",
                "Events must be a non-empty array",
                400
            )
            return jsonify(response), status
        
        # Process and store events
        stored_events = []
        errors = []
        
        for i, event_data in enumerate(events_data):
            try:
                # Create analytics event
                event = create_analytics_event_from_data(event_data)
                event_id = analytics_repo.store_event(event)
                stored_events.append(event_id)
                
            except Exception as e:
                errors.append({
                    'index': i,
                    'error': str(e),
                    'event_data': event_data
                })
                logging.error(f"Error processing event {i}: {str(e)}")
        
        # Log batch processing results
        logging.info(f"Analytics batch processed: {len(stored_events)} stored, {len(errors)} errors")
        
        response_data = {
            'stored_count': len(stored_events),
            'error_count': len(errors),
            'batch_id': batch_info.get('batch_id'),
            'stored_event_ids': stored_events
        }
        
        if errors:
            response_data['errors'] = errors
        
        return jsonify(success_response(
            response_data,
            f"Processed {len(stored_events)} analytics events"
        )), 200
        
    except Exception as e:
        logging.error(f"Error storing analytics events: {str(e)}")
        response, status = create_error_response(
            "ANALYTICS_003",
            "Failed to store analytics events",
            500
        )
        return jsonify(response), status


@analytics_bp.route('/business-metrics', methods=['POST'])
def track_business_metrics():
    """
    Track Romanian marketplace business metrics.
    """
    try:
        data = request.get_json()
        if not data:
            response, status = create_error_response(
                "ANALYTICS_004",
                "Business metrics data is required",
                400
            )
            return jsonify(response), status
        
        # Create business KPI
        kpi = BusinessKPI(
            kpi_name=data.get('metric_name', ''),
            kpi_value=float(data.get('metric_value', 0)),
            timestamp=parse_timestamp(data.get('timestamp')),
            time_period=data.get('time_period', 'daily'),
            market=data.get('market', 'romania'),
            currency=data.get('currency', 'RON'),
            category=data.get('category', ''),
            additional_data=data.get('additional_data', {})
        )
        
        kpi_id = analytics_repo.store_business_kpi(kpi)
        
        logging.info(f"Business metric tracked: {kpi.kpi_name} = {kpi.kpi_value}")
        
        return jsonify(success_response(
            {'kpi_id': kpi_id},
            "Business metric tracked successfully"
        )), 200
        
    except Exception as e:
        logging.error(f"Error tracking business metrics: {str(e)}")
        response, status = create_error_response(
            "ANALYTICS_005",
            "Failed to track business metrics",
            500
        )
        return jsonify(response), status


@analytics_bp.route('/user-journey', methods=['POST'])
def track_user_journey():
    """
    Track user journey step.
    """
    try:
        data = request.get_json()
        if not data:
            response, status = create_error_response(
                "ANALYTICS_006",
                "Journey data is required",
                400
            )
            return jsonify(response), status
        
        # Create journey step
        step = UserJourneyStep(
            step_name=data.get('step_name', ''),
            step_order=int(data.get('step_order', 0)),
            timestamp=parse_timestamp(data.get('timestamp')),
            session_id=data.get('session_id', ''),
            page_url=data.get('page_url', ''),
            action_type=data.get('action_type', ''),
            duration_ms=data.get('duration_ms'),
            data=data.get('data', {})
        )
        
        step_id = analytics_repo.store_journey_step(step)
        
        return jsonify(success_response(
            {'step_id': step_id},
            "Journey step tracked successfully"
        )), 200
        
    except Exception as e:
        logging.error(f"Error tracking user journey: {str(e)}")
        response, status = create_error_response(
            "ANALYTICS_007",
            "Failed to track user journey",
            500
        )
        return jsonify(response), status


@analytics_bp.route('/performance', methods=['POST'])
def track_performance():
    """
    Track performance metrics.
    """
    try:
        data = request.get_json()
        if not data:
            response, status = create_error_response(
                "ANALYTICS_008",
                "Performance data is required",
                400
            )
            return jsonify(response), status
        
        # Create performance metric
        metric = PerformanceMetric(
            metric_name=data.get('metric_name', ''),
            metric_value=float(data.get('metric_value', 0)),
            metric_unit=data.get('metric_unit', ''),
            timestamp=parse_timestamp(data.get('timestamp')),
            page_url=data.get('page_url', ''),
            user_agent=data.get('user_agent', ''),
            connection_type=data.get('connection_type', ''),
            device_type=data.get('device_type', '')
        )
        
        metric_id = analytics_repo.store_performance_metric(metric)
        
        return jsonify(success_response(
            {'metric_id': metric_id},
            "Performance metric tracked successfully"
        )), 200
        
    except Exception as e:
        logging.error(f"Error tracking performance: {str(e)}")
        response, status = create_error_response(
            "ANALYTICS_009",
            "Failed to track performance",
            500
        )
        return jsonify(response), status


@analytics_bp.route('/conversions', methods=['POST'])
def track_conversion():
    """
    Track conversion events.
    """
    try:
        data = request.get_json()
        if not data:
            response, status = create_error_response(
                "ANALYTICS_010",
                "Conversion data is required",
                400
            )
            return jsonify(response), status
        
        # Create conversion event
        event = EcommerceEvent(
            event_type='conversion',
            event_category='Conversie',
            event_action=data.get('conversion_type', ''),
            timestamp=parse_timestamp(data.get('timestamp')),
            session_id=data.get('session_id', ''),
            page_url=data.get('page_url', ''),
            transaction_id=data.get('transaction_id'),
            revenue=float(data.get('revenue', 0)),
            currency=data.get('currency', 'RON'),
            data=data.get('additional_data', {})
        )
        
        event_id = analytics_repo.store_event(event)
        
        return jsonify(success_response(
            {'event_id': event_id},
            "Conversion tracked successfully"
        )), 200
        
    except Exception as e:
        logging.error(f"Error tracking conversion: {str(e)}")
        response, status = create_error_response(
            "ANALYTICS_011",
            "Failed to track conversion",
            500
        )
        return jsonify(response), status


@analytics_bp.route('/dashboard', methods=['GET'])
@require_admin_auth
def get_dashboard_data():
    """
    Get analytics dashboard data for admin users.
    """
    try:
        # Parse query parameters
        time_range = request.args.get('time_range', '7d')
        metrics = request.args.get('metrics', '').split(',') if request.args.get('metrics') else []
        timezone_str = request.args.get('timezone', 'Europe/Bucharest')
        
        # Calculate date range
        start_date, end_date = parse_time_range(time_range)
        
        # Get analytics summary
        summary = analytics_repo.get_analytics_summary(start_date, end_date)
        
        # Get Romanian marketplace metrics
        marketplace_metrics = analytics_repo.get_romanian_marketplace_metrics(start_date, end_date)
        
        # Get conversion funnel
        conversion_funnel = analytics_repo.get_conversion_funnel(start_date, end_date)
        
        # Get performance metrics if requested
        performance_data = []
        if 'performance' in metrics:
            performance_data = analytics_repo.get_performance_metrics({
                'start_date': start_date,
                'end_date': end_date
            }, limit=1000)
        
        # Get business KPIs if requested
        kpi_data = []
        if 'kpis' in metrics:
            kpi_data = analytics_repo.get_business_kpis({
                'start_date': start_date,
                'end_date': end_date
            })
        
        dashboard_data = {
            'summary': summary,
            'marketplace_metrics': marketplace_metrics,
            'conversion_funnel': conversion_funnel,
            'performance_data': performance_data,
            'business_kpis': kpi_data,
            'time_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'range': time_range
            }
        }
        
        return jsonify(success_response(
            dashboard_data,
            "Dashboard data retrieved successfully"
        )), 200
        
    except Exception as e:
        logging.error(f"Error getting dashboard data: {str(e)}")
        response, status = create_error_response(
            "ANALYTICS_012",
            "Failed to retrieve dashboard data",
            500
        )
        return jsonify(response), status


@analytics_bp.route('/realtime', methods=['GET'])
@require_admin_auth
def get_realtime_data():
    """
    Get real-time analytics data.
    """
    try:
        # Get events from last 30 minutes
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(minutes=30)
        
        # Get recent events
        recent_events = analytics_repo.get_events({
            'start_date': start_time,
            'end_date': end_time
        }, limit=100)
        
        # Get active sessions (last 5 minutes)
        active_start = end_time - timedelta(minutes=5)
        active_events = analytics_repo.get_events({
            'start_date': active_start,
            'end_date': end_time
        }, limit=50)
        
        # Count unique sessions
        active_sessions = set()
        for event in active_events:
            if event.get('session_id'):
                active_sessions.add(event['session_id'])
        
        # Get performance metrics from last hour
        perf_start = end_time - timedelta(hours=1)
        performance_metrics = analytics_repo.get_performance_metrics({
            'start_date': perf_start,
            'end_date': end_time
        }, limit=100)
        
        realtime_data = {
            'active_users': len(active_sessions),
            'recent_events_count': len(recent_events),
            'recent_events': recent_events[:20],  # Latest 20 events
            'performance_metrics': performance_metrics[-10:],  # Latest 10 metrics
            'last_updated': end_time.isoformat(),
            'time_range': {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            }
        }
        
        return jsonify(success_response(
            realtime_data,
            "Real-time data retrieved successfully"
        )), 200
        
    except Exception as e:
        logging.error(f"Error getting real-time data: {str(e)}")
        response, status = create_error_response(
            "ANALYTICS_013",
            "Failed to retrieve real-time data",
            500
        )
        return jsonify(response), status


@analytics_bp.route('/romanian-kpis', methods=['POST'])
def track_romanian_kpis():
    """
    Track Romanian marketplace specific KPIs.
    """
    try:
        data = request.get_json()
        if not data:
            response, status = create_error_response(
                "ANALYTICS_014",
                "Romanian KPI data is required",
                400
            )
            return jsonify(response), status
        
        # Store multiple KPIs for Romanian business context
        kpi_ids = []
        
        # Producer engagement KPI
        if 'producer_engagement' in data:
            kpi = BusinessKPI(
                kpi_name='producer_engagement',
                kpi_value=float(data['producer_engagement']),
                timestamp=parse_timestamp(data.get('timestamp')),
                time_period='daily',
                market='romania',
                currency='RON',
                category='business',
                additional_data=data.get('business_context', {})
            )
            kpi_ids.append(analytics_repo.store_business_kpi(kpi))
        
        # Local product popularity
        if 'local_product_score' in data:
            kpi = BusinessKPI(
                kpi_name='local_product_popularity',
                kpi_value=float(data['local_product_score']),
                timestamp=parse_timestamp(data.get('timestamp')),
                time_period='daily',
                market='romania',
                currency='RON',
                category='product',
                additional_data=data.get('business_context', {})
            )
            kpi_ids.append(analytics_repo.store_business_kpi(kpi))
        
        # Romanian customer satisfaction
        if 'customer_satisfaction' in data:
            kpi = BusinessKPI(
                kpi_name='romanian_customer_satisfaction',
                kpi_value=float(data['customer_satisfaction']),
                timestamp=parse_timestamp(data.get('timestamp')),
                time_period='weekly',
                market='romania',
                currency='RON',
                category='customer',
                additional_data=data.get('business_context', {})
            )
            kpi_ids.append(analytics_repo.store_business_kpi(kpi))
        
        return jsonify(success_response(
            {'kpi_ids': kpi_ids},
            "Romanian KPIs tracked successfully"
        )), 200
        
    except Exception as e:
        logging.error(f"Error tracking Romanian KPIs: {str(e)}")
        response, status = create_error_response(
            "ANALYTICS_015",
            "Failed to track Romanian KPIs",
            500
        )
        return jsonify(response), status


@analytics_bp.route('/export', methods=['GET'])
@require_admin_auth
def export_analytics_data():
    """
    Export analytics data in various formats.
    """
    try:
        # Parse parameters
        format_type = request.args.get('format', 'json')
        time_range = request.args.get('time_range', '30d')
        event_category = request.args.get('event_category')
        
        # Calculate date range
        start_date, end_date = parse_time_range(time_range)
        
        # Build filters
        filters = {
            'start_date': start_date,
            'end_date': end_date
        }
        
        if event_category:
            filters['event_category'] = event_category
        
        # Get events
        events = analytics_repo.get_events(filters, limit=10000)
        
        if format_type == 'csv':
            # Convert to CSV
            csv_data = convert_events_to_csv(events)
            
            return Response(
                csv_data,
                mimetype='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename=analytics_export_{time_range}.csv'
                }
            )
        else:
            # Return JSON
            export_data = {
                'events': events,
                'export_info': {
                    'format': format_type,
                    'time_range': time_range,
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'event_count': len(events),
                    'filters_applied': filters
                }
            }
            
            return jsonify(success_response(
                export_data,
                f"Analytics data exported successfully ({len(events)} events)"
            )), 200
        
    except Exception as e:
        logging.error(f"Error exporting analytics data: {str(e)}")
        response, status = create_error_response(
            "ANALYTICS_016",
            "Failed to export analytics data",
            500
        )
        return jsonify(response), status


# Helper functions

def create_analytics_event_from_data(event_data: Dict[str, Any]) -> AnalyticsEvent:
    """Create analytics event from request data"""
    
    # Determine event type
    if event_data.get('event_type') == 'ecommerce':
        return EcommerceEvent(
            event_type=event_data.get('event_type', ''),
            event_category=event_data.get('event_category', ''),
            event_action=event_data.get('event_action', ''),
            timestamp=parse_timestamp(event_data.get('timestamp')),
            session_id=event_data.get('session_id', ''),
            user_id=event_data.get('user_id'),
            page_url=event_data.get('page_url', ''),
            referrer=event_data.get('referrer', ''),
            user_agent=event_data.get('user_agent', ''),
            ip_address=get_client_ip(),
            product_id=event_data.get('product_id'),
            product_name=event_data.get('product_name', ''),
            product_category=event_data.get('product_category', ''),
            producer_name=event_data.get('producer_name', ''),
            price=float(event_data.get('price', 0)),
            quantity=int(event_data.get('quantity', 1)),
            currency=event_data.get('currency', 'RON'),
            transaction_id=event_data.get('transaction_id'),
            revenue=float(event_data.get('revenue', 0)),
            data=event_data.get('data', {})
        )
    else:
        return AnalyticsEvent(
            event_type=event_data.get('event_type', ''),
            event_category=event_data.get('event_category', ''),
            event_action=event_data.get('event_action', ''),
            timestamp=parse_timestamp(event_data.get('timestamp')),
            session_id=event_data.get('session_id', ''),
            user_id=event_data.get('user_id'),
            page_url=event_data.get('page_url', ''),
            referrer=event_data.get('referrer', ''),
            user_agent=event_data.get('user_agent', ''),
            ip_address=get_client_ip(),
            data=event_data.get('data', {})
        )


def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse timestamp string to datetime object"""
    if not timestamp_str:
        return datetime.now(timezone.utc)
    
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except Exception:
        return datetime.now(timezone.utc)


def parse_time_range(time_range: str) -> tuple:
    """Parse time range string to start and end dates"""
    end_date = datetime.now(timezone.utc)
    
    if time_range == '1d':
        start_date = end_date - timedelta(days=1)
    elif time_range == '7d':
        start_date = end_date - timedelta(days=7)
    elif time_range == '30d':
        start_date = end_date - timedelta(days=30)
    elif time_range == '90d':
        start_date = end_date - timedelta(days=90)
    elif time_range == '1y':
        start_date = end_date - timedelta(days=365)
    else:
        start_date = end_date - timedelta(days=7)
    
    return start_date, end_date


def get_client_ip() -> str:
    """Get client IP address from request"""
    try:
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr or ''
    except Exception:
        return ''


def convert_events_to_csv(events: List[Dict[str, Any]]) -> str:
    """Convert events list to CSV format"""
    import csv
    import io
    
    if not events:
        return "No data available"
    
    output = io.StringIO()
    
    # Get all possible fields from events
    all_fields = set()
    for event in events:
        all_fields.update(event.keys())
    
    fieldnames = sorted(list(all_fields))
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for event in events:
        # Convert ObjectId to string
        if '_id' in event:
            event['_id'] = str(event['_id'])
        writer.writerow(event)
    
    return output.getvalue()