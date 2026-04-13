---
name: odoo-hr-skill
description: Odoo 人力资源 Skill - 提供员工档案管理、部门管理、职位管理、考勤管理 (打卡记录/考勤统计/异常处理)、假期管理 (假期类型/申请审批/余额计算) 功能。Use when working with Odoo HR modules for: (1) Employee management, (2) Department and job position management, (3) Attendance tracking, (4) Leave management and approval, (5) HR reporting and analytics.
---

# Odoo 人力资源 Skill

## 快速开始

### 认证配置

```bash
export ODOO_URL="https://your-company.odoo.com"
export ODOO_DB="your_database"
export ODOO_API_KEY="your_api_key"
```

### 基础用法

```bash
# 查询员工列表
odoo-hr list-employees --department "技术部"

# 创建请假申请
odoo-hr create-leave --employee 1 --type annual --days 5

# 查看考勤统计
odoo-hr attendance-report --month 2026-04
```

## 核心功能

### 1. 员工档案管理

#### 创建员工

```python
employee_data = {
    'name': '张三',
    'work_email': 'zhangsan@company.com',
    'work_phone': '13800138000',
    'department_id': dept_id,
    'job_id': job_id,
    'contract_id': contract_id,
    'birthday': '1990-01-01',
    'gender': 'male'
}
employee_id = odoo.execute_kw(db, uid, api_key, 'hr.employee', 'create', [employee_data])
```

#### 查询员工

```python
domain = [['department_id', '=', dept_id]]
fields = ['name', 'work_email', 'job_title', 'phone']
employees = odoo.execute_kw(db, uid, api_key, 'hr.employee', 'search_read', [domain], {'fields': fields})
```

### 2. 考勤管理

#### 打卡记录

```python
# 创建打卡记录
attendance_data = {
    'employee_id': employee_id,
    'check_in': '2026-04-12 09:00:00',
    'check_out': '2026-04-12 18:00:00',
    'worked_hours': 8.0
}
attendance_id = odoo.execute_kw(db, uid, api_key, 'hr.attendance', 'create', [attendance_data])
```

#### 考勤统计

```python
def get_attendance_summary(odoo, db, uid, api_key, employee_id, month):
    """获取考勤统计"""
    domain = [
        ['employee_id', '=', employee_id],
        ['check_in', '>=', f'{month}-01'],
        ['check_in', '<=', f'{month}-31']
    ]
    attendances = odoo.execute_kw(db, uid, api_key, 'hr.attendance', 'search_read', [domain])
    
    total_hours = sum(att.get('worked_hours', 0) for att in attendances)
    work_days = len(set(att['check_in'][:10] for att in attendances))
    
    return {
        'employee_id': employee_id,
        'month': month,
        'work_days': work_days,
        'total_hours': total_hours,
        'avg_hours_per_day': total_hours / work_days if work_days else 0
    }
```

### 3. 假期管理

#### 创建请假申请

```python
leave_data = {
    'employee_id': employee_id,
    'holiday_status_id': leave_type_id,
    'date_from': '2026-04-15',
    'date_to': '2026-04-19',
    'number_of_days': 5,
    'reason': '年假'
}
leave_id = odoo.execute_kw(db, uid, api_key, 'hr.leave', 'create', [leave_data])
```

#### 审批流程

```python
# 提交审批
odoo.execute_kw(db, uid, api_key, 'hr.leave', 'action_validate', [[leave_id]])

# 拒绝申请
odoo.execute_kw(db, uid, api_key, 'hr.leave', 'action_refuse', [[leave_id]])

# 撤销
odoo.execute_kw(db, uid, api_key, 'hr.leave', 'action_cancel', [[leave_id]])
```

#### 假期余额计算

```python
def get_leave_balance(odoo, db, uid, api_key, employee_id, leave_type_id):
    """获取假期余额"""
    # 获取已批准假期
    approved_domain = [
        ['employee_id', '=', employee_id],
        ['holiday_status_id', '=', leave_type_id],
        ['state', '=', 'validate')
    ]
    approved_leaves = odoo.execute_kw(db, uid, api_key, 'hr.leave', 'search_read', [approved_domain])
    used_days = sum(leave.get('number_of_days', 0) for leave in approved_leaves)
    
    # 获取假期分配
    allocation_domain = [
        ['employee_id', '=', employee_id],
        ['holiday_status_id', '=', leave_type_id],
        ['state', '=', 'validate')
    ]
    allocations = odoo.execute_kw(db, uid, api_key, 'hr.leave.allocation', 'search_read', [allocation_domain])
    total_days = sum(alloc.get('number_of_days', 0) for alloc in allocations)
    
    return {
        'employee_id': employee_id,
        'leave_type': leave_type_id,
        'total_days': total_days,
        'used_days': used_days,
        'remaining_days': total_days - used_days
    }
```

## 脚本工具

### 批量导入员工

```bash
python scripts/import_employees.py --file employees.csv
```

### 生成考勤报表

```bash
python scripts/attendance_report.py --month 2026-04 --format excel
```

### 假期余额导出

```bash
python scripts/export_leave_balance.py --department all
```

## 最佳实践

- 定期同步考勤数据
- 及时审批请假申请
- 定期备份员工档案

## 支持的 Odoo 版本

- Odoo 16.0 LTS
- Odoo 17.0 LTS
- Odoo 18.0 (最新)

---

*Skill 版本：1.0.0*
*最后更新：2026-04-12*
