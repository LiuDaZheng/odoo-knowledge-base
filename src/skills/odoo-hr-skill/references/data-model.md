# HR 模块数据模型

## ER 关系图

```mermaid
erDiagram
    hr_department ||--o{ hr_employee : "部门包含员工"
    hr_department ||--o{ hr_department : "上级部门"
    hr_job ||--o{ hr_employee : "职位聘用员工"
    hr_department ||--o{ hr_job : "部门定义职位"
    hr_employee ||--o{ hr_employee : "上级管理"
    hr_employee ||--o{ hr_attendance : "员工考勤"
    hr_employee ||--o{ hr_leave : "申请假期"
    hr_leave_type ||--o{ hr_leave : "类型定义"
    hr_department ||--|| hr_employee : "部门经理"

    hr_department {
        int id PK
        string name
        int parent_id FK "上级部门"
        int manager_id FK "部门经理"
        bool active
        datetime create_date
    }

    hr_employee {
        int id PK
        string name
        int department_id FK
        int job_id FK
        int parent_id FK "上级"
        int address_home_id FK "家庭地址"
        bool active
        datetime create_date
    }

    hr_job {
        int id PK
        string name
        int department_id FK
        int no_of_recruitment
        int expected_employees
        bool active
    }

    hr_attendance {
        int id PK
        int employee_id FK
        datetime check_in
        datetime check_out
        float worked_hours
        bool active
    }

    hr_leave_type {
        int id PK
        string name
        string allocation_type "fixed/offering"
        string leave_validation_type "no_validation/manager/both"
        string time_type "leave/work_time"
        bool active
    }

    hr_leave {
        int id PK
        int employee_id FK
        int holiday_status_id FK
        datetime date_from
        datetime date_to
        string state "draft/confirm/validate/refuse/cancel"
        float number_of_days
        string type "remove/add_deduction"
    }
}
```

## 核心表字段说明

### hr.department（部门）

| 字段名 | 类型 | 说明 | 业务含义 |
|--------|------|------|---------|
| id | integer | 主键 | 部门唯一标识 |
| name | char(64) | 部门名称 | 如"研发部"、"销售部" |
| parent_id | integer | 上级部门ID | 支持多层级部门架构 |
| manager_id | integer | 部门经理 | 指向 hr.employee，管理者双重身份 |
| active | boolean | 是否激活 | 逻辑删除控制 |
| create_date | datetime | 创建时间 | 记录创建时间戳 |

### hr.employee（员工）

| 字段名 | 类型 | 说明 | 业务含义 |
|--------|------|------|---------|
| id | integer | 主键 | 员工唯一标识 |
| name | char(128) | 员工姓名 | 公开显示名称 |
| department_id | integer | 所属部门 | 归属组织单元 |
| job_id | integer | 职位ID | 对应岗位名称 |
| parent_id | integer | 直接上级 | 汇报线管理 |
| address_home_id | integer | 家庭地址 | 关联联系人/地址 |
| active | boolean | 是否激活 | 员工状态开关 |
| create_date | datetime | 入职日期 | 入职时间记录 |

### hr.job（职位）

| 字段名 | 类型 | 说明 | 业务含义 |
|--------|------|------|---------|
| id | integer | 主键 | 职位唯一标识 |
| name | char(128) | 职位名称 | 如"高级工程师"、"经理" |
| department_id | integer | 所属部门 | 职位归属 |
| no_of_recruitment | integer | 招聘人数 | 当前正在招聘的职位数 |
| expected_employees | integer | 预期员工数 | 编制人数 |
| active | boolean | 是否激活 | 职位状态 |

### hr.attendance（考勤记录）

| 字段名 | 类型 | 说明 | 业务含义 |
|--------|------|------|---------|
| id | integer | 主键 | 记录唯一标识 |
| employee_id | integer | 员工ID | 打卡员工 |
| check_in | datetime | 上班打卡时间 | 签到时刻 |
| check_out | datetime | 下班打卡时间 | 签退时刻（可为空表示未签退） |
| worked_hours | float | 工作时长 | 自动计算：check_out - check_in |
| active | boolean | 有效记录 | 考勤有效状态 |

### hr.leave（假期申请）

| 字段名 | 类型 | 说明 | 业务含义 |
|--------|------|------|---------|
| id | integer | 主键 | 申请唯一标识 |
| employee_id | integer | 申请人 | 提交假期的员工 |
| holiday_status_id | integer | 假期类型 | 关联假期类型 |
| date_from | datetime | 开始日期 | 假期起始 |
| date_to | datetime | 结束日期 | 假期结束 |
| state | selection | 审批状态 | draft/confirm/validate/refuse/cancel |
| number_of_days | float | 假期天数 | 按日计算，含半日处理 |
| type | selection | 类型 | remove=请假, add_deduction=补休 |

### hr.leave.type（假期类型）

| 字段名 | 类型 | 说明 | 业务含义 |
|--------|------|------|---------|
| id | integer | 主键 | 类型唯一标识 |
| name | char(128) | 假期名称 | 如"年假"、"病假"、"婚假" |
| allocation_type | selection | 分配方式 | fixed(固定额度)/offering(按需分配) |
| leave_validation_type | selection | 审批方式 | no_validation/manager/both |
| time_type | selection | 时间类型 | leave(假期)/work_time(工作时段) |
| active | boolean | 有效 | 假期类型开关 |

## 业务场景映射

### 数据流转

```
┌─────────────┐     ┌─────────────┐     ┌────────────────┐
│ hr.job      │────▶│ hr.employee │────▶│ hr.attendance  │
│ (职位编制)  │     │ (员工入职)  │     │ (每日打卡)     │
└─────────────┘     └──────┬──────┘     └────────────────┘
                          │
       ┌──────────────────┼──────────────────┐
       ▼                  ▼                  ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────────┐
│hr.department│   │ hr.leave.type│   │ hr.leave        │
│ (部门架构)  │   │ (假期类型)  │   │ (假期申请/审批) │
└─────────────┘   └─────────────┘   └─────────────────┘
```

### 核心业务流程

1. **员工档案建立**
   - 创建 `hr.employee` 记录
   - 分配 `department_id` 和 `job_id`
   - 设置汇报关系 `parent_id`

2. **部门/职位分配**
   - 部门经理通过 `manager_id` 关联
   - 职位编制控制招聘 `no_of_recruitment`

3. **每日打卡考勤**
   - 员工通过 `hr.attendance` 记录出勤
   - 系统自动计算 `worked_hours`
   - 支持外勤、出差等特殊考勤

4. **假期申请审批**
   - 员工提交 `hr.leave`（state=draft → confirm）
   - 经理审批（state=confirm → validate 或 refuse）
   - 系统根据 `holiday_status_id` 扣减余额

5. **假期余额扣减**
   - 审批通过后，根据 `number_of_days` 扣减 `hr.leave.type` 分配的额度
   - 支持按小时/按天请假
