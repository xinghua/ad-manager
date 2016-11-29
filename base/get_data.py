# -*- coding: utf8 -*-
from base.connection import get_cursor
import datetime

head_list1 = ['日期','新增']
head_list1.extend(range(2,91))

head_list2 = ['日期','新增']
head_list2.extend(range(1,91))

head_list3 = ['日期']
head_list3.extend(range(1,61))

#如果有分布维度，则把维度当做表头
widget_config = {
    1:{'index_list':[1,2,3,4,5,6],
       'table_head_list':['日期','点击','唯一点击','激活','注册','新增','有效新增'],
       'name': '新增效果',
    },
    2:{'index_list':[5,8],
       'table_head_list':head_list1,
       'name': '新增留存',
       'distribution_dim':{
        'dim':0,
        'index_id':8,
        'dim_value_list':range(2,91)
        }
    },
    3:{'index_list':[5,7],
       'table_head_list':head_list1,
       'name': '新增ltv',
       'distribution_dim':{
        'dim':0,
        'index_id':7,
        'dim_value_list':range(1,91)
        }
    },
    4:{'index_list':[5,9],
       'table_head_list':head_list1,
       'name': '新增充值额',
       'distribution_dim':{
        'dim':0,
        'index_id':9,
        'dim_value_list':range(1,91)
        }
    },
    5:{'index_list':[5,10],
       'table_head_list':head_list1,
       'name': '新增充值率',
       'distribution_dim':{
        'dim':0,
        'index_id':10,
        'dim_value_list':range(1,91)
        }
    },
    6:{'index_list':[5],
       'table_head_list':['日期','[0,30)分钟','[30,60)分钟','[60,90)分钟','[90,120)分钟','[120,180)分钟','[180,360)分钟','[360,+∞)分钟'],
       'name': '线时长分布',
       'distribution_dim':{
        'dim':2,
        'index_id':5,
        'dim_value_list':range(1,8)
        }
    },
    7:{'index_list':[5],
       'table_head_list':head_list3,
       'name': '等级分布',
       'distribution_dim':{
        'dim':3,
        'index_id':5,
        'dim_value_list':range(1,61)
        }
    },
    8:{'index_list':[1,2,15,11,12],
       'table_head_list':['日期','点击','唯一点击','激活（未限制）','注册（未限制）','新增（未限制）'],
       'name': '新增效果（未限制）',
    },                              
}

def get_data(begin_date, end_date, game_alias, dim_dict, widget_id):
    cursor = get_cursor()
    begin_date_id = begin_date.strftime('%Y%m%d')
    end_date_id = end_date.strftime('%Y%m%d')
    
    if 4 in dim_dict and 5 in dim_dict:
        cursor.execute("select count(1) from ad_manager.channel where id=%s and media_type=%s"%(dim_dict[5], dim_dict[4]))
        count = cursor.fetchone()[0]
        if count == 0:
            return widget_config[widget_id]['table_head_list'], []
        else:
            del dim_dict[4]

    dim_type_list = dim_dict.keys()    
    dim_type_list.sort()
    table_name = "dw.dw_%s_day" % (game_alias)
    for dim_type in dim_type_list:
        table_name += "_%s" % dim_type
        
    where_sql = '1=1'
    for dim in dim_dict:
        where_sql += ' and dim_%s = %s'%(dim, dim_dict[dim])
        
    index_list_str = ','.join(map(str, widget_config[widget_id]['index_list']))
        
    if 4 in dim_dict and 5 not in dim_dict:
        base_table_name = "dw.dw_%s_day" % (game_alias)
        for dim_type in dim_type_list:
            if dim_type == 4:
                base_table_name += "_5"
            else:
                base_table_name += "_%s" % dim_type
        
        cursor.execute("""
        create temporary table %s(
        date_id bigint,
        index_id int,
        index_value double
        )
        """%table_name)
        cursor.execute("""
        insert into %s select date_id, index_id, sum(index_value)
        from %s a, ad_manager.channel b, ad_manager.base_index c 
        where %s and date_id between %s and %s and a.dim_5 = b.id and index_id in (%s) 
        and index_id = c.id and c.is_accumulated=1
        group by date_id, index_id
        """%(table_name, base_table_name, where_sql.replace('dim_4', 'b.media_type'), begin_date_id, end_date_id, index_list_str))
        
        cursor.execute("""
        insert into %s 
        select aa.date_id, aa.id, aa.v/bb.v
        (select date_id, c.id, sum(index_value) as v 
        from %s a, ad_manager.channel b, ad_manager.base_index c 
        where %s and date_id between %s and %s and a.dim_5 = b.id and c.id in (%s) 
        and index_id = c.numerator and c.is_accumulated=0 
        group by date_id, c.id) aa, 
        (select date_id, c.id, sum(index_value) as v  
        from %s a, ad_manager.channel b, ad_manager.base_index c 
        where %s and date_id between %s and %s and a.dim_5 = b.id and c.id in (%s) 
        and index_id = c.denominator and c.is_accumulated=0 
        group by date_id, c.id) bb 
        where aa.id = bb.id and aa.date_id=bb.date_id 
        """%(table_name, base_table_name, where_sql.replace('dim_4', 'b.media_type'), begin_date_id, end_date_id, index_list_str,\
             base_table_name, where_sql.replace('dim_4', 'b.media_type'), begin_date_id, end_date_id, index_list_str))
        where_sql = '1=1'
        
    cursor.execute("""
    select date_id, index_id, index_value from %s where %s and index_id in (%s) and date_id between %s and %s
    """%(table_name, where_sql, index_list_str, begin_date_id, end_date_id))
    datas = cursor.fetchall()
    data_dict = {}
    for data in datas:
        data_dict[(data[0], data[1])] = data[2]
    
    cursor.execute("""
    select index_id, sum(index_value) from %s a, ad_manager.base_index b 
    where a.index_id = b.id and is_accumulated=1 and %s and index_id in (%s) and date_id between %s and %s group by index_id
    union all 
    select aa.id, aa.v/bb.v from 
    (select c.id, sum(index_value) as v 
    from %s a, ad_manager.base_index c 
    where %s and c.id in (%s) and date_id between %s and %s 
    and index_id = c.numerator and c.is_accumulated=0 
    group by c.id) aa, 
    (select c.id, sum(index_value) as v  
    from %s a, ad_manager.base_index c 
    where %s and c.id in (%s) and date_id between %s and %s
    and index_id = c.denominator and c.is_accumulated=0 
    group by c.id) bb 
    where aa.id = bb.id
    """%(table_name, where_sql, index_list_str, begin_date_id, end_date_id,\
         table_name, where_sql, index_list_str, begin_date_id, end_date_id,\
         table_name, where_sql, index_list_str, begin_date_id, end_date_id))
    datas = cursor.fetchall()
    data_summary_dict = {}
    for data in datas:
        data_summary_dict[data[0]] = data[1]
        
    return_list = []
    if 'distribution_dim' not in widget_config[widget_id]:
        day_summary_list =['汇总']
        for index_id in widget_config[widget_id]['index_list']:
            if index_id in data_summary_dict:
                day_summary_list.append(data_summary_dict[index_id])
            else:
                day_summary_list.append('-')
        return_list.append(day_summary_list)
        while begin_date <= end_date:
            date_id = int(begin_date.strftime('%Y%m%d'))
            day_list = [date_id]
            for index_id in widget_config[widget_id]['index_list']:
                if (date_id, index_id) in data_dict:
                    day_list.append(data_dict[(date_id, index_id)])
                else:
                    day_list.append('-')
            return_list.append(day_list)
            begin_date += datetime.timedelta(days=1)
    else:
        distribution_dim = widget_config[widget_id]['distribution_dim']['dim']
        distribution_index = widget_config[widget_id]['distribution_dim']['index_id']
        dim_type_list.append(distribution_dim)
        dim_type_list.sort()
        table_name = "dw.dw_%s_day" % (game_alias)
        for dim_type in dim_type_list:
            table_name += "_%s" % dim_type
            
        if 4 in dim_dict and 5 not in dim_dict:
            base_table_name = "dw.dw_%s_day" % (game_alias)
            for dim_type in dim_type_list:
                if dim_type == 4:
                    base_table_name += "_5"
                else:
                    base_table_name += "_%s" % dim_type
            
            cursor.execute("""
            create temporary table %s(
            date_id bigint,
            index_id int,
            index_value double,
            dim_%s int
            )
            """%(table_name, distribution_dim))
            cursor.execute("""
            insert into %s select date_id, index_id, sum(index_value), dim_%s
            from %s a, ad_manager.channel b, ad_manager.base_index c 
            where %s and date_id between %s and %s and a.dim_5 = b.id and index_id in (%s) 
            and index_id = c.id and c.is_accumulated=1
            group by date_id, index_id, dim_%s
            """%(table_name, distribution_dim, base_table_name, where_sql.replace('dim_4', 'b.media_type'), \
                 begin_date_id, end_date_id, index_list_str, distribution_dim))
            
            cursor.execute("""
            insert into %s 
            select aa.date_id, aa.id, aa.v/bb.v, dim_%s from 
            (select date_id, c.id, sum(index_value) as v, dim_%s 
            from %s a, ad_manager.channel b, ad_manager.base_index c 
            where %s and date_id between %s and %s and a.dim_5 = b.id and c.id in (%s) 
            and index_id = c.numerator and c.is_accumulated=0 
            group by date_id, c.id, dim_%s) aa, 
            (select date_id, c.id, sum(index_value) as v, dim_%s  
            from %s a, ad_manager.channel b, ad_manager.base_index c 
            where %s and date_id between %s and %s and a.dim_5 = b.id and c.id in (%s) 
            and index_id = c.denominator and c.is_accumulated=0 
            group by date_id, c.id, dim_%s) bb 
            where aa.id = bb.id and aa.date_id=bb.date_id and aa.dim_%s=bb.dim_%s
            """%(table_name, distribution_dim, distribution_dim, base_table_name, where_sql.replace('dim_4', 'b.media_type'), \
                 begin_date_id, end_date_id, index_list_str, distribution_dim, distribution_dim, base_table_name, where_sql.replace('dim_4', 'b.media_type'), \
                 begin_date_id, end_date_id, index_list_str, distribution_dim))
            where_sql = '1=1'
        
        cursor.execute("""
        select date_id, dim_%s, index_value from %s where %s and index_id = %s and date_id between %s and %s
        """%(distribution_dim, table_name, where_sql,  distribution_index, begin_date_id, end_date_id))
        datas = cursor.fetchall()
        data_dict2 = {}
        for data in datas:
            data_dict2[(data[0], data[1])] = data[2]
            
        print """
        select dim_%s as dim_id, sum(index_value) from %s a, ad_manager.base_index b 
        where a.index_id = b.id and is_accumulated=1 and %s and index_id = %s and date_id between %s and %s group by dim_id
        union all 
        select aa.dim_id, aa.v/bb.v from 
        (select dim_%s as dim_id, sum(index_value) as v 
        from %s a, ad_manager.base_index c 
        where %s and c.id = %s and date_id between %s and %s 
        and index_id = c.numerator and c.is_accumulated=0 
        group by dim_id) aa, 
        (select dim_%s as dim_id, sum(index_value) as v  
        from %s a, ad_manager.base_index c 
        where %s and c.id = %s and date_id between %s and %s
        and index_id = c.denominator and c.is_accumulated=0 
        group by dim_id) bb 
        where aa.dim_id = bb.dim_id
        """%(distribution_dim, table_name, where_sql, distribution_index, begin_date_id, end_date_id,\
             distribution_dim, table_name, where_sql, distribution_index, begin_date_id, end_date_id,\
             distribution_dim, table_name, where_sql, distribution_index, begin_date_id, end_date_id)
        
        cursor.execute("""
        select dim_%s as dim_id, sum(index_value) from %s a, ad_manager.base_index b 
        where a.index_id = b.id and is_accumulated=1 and %s and index_id = %s and date_id between %s and %s group by dim_id
        union all 
        select aa.dim_id, aa.v/bb.v from 
        (select dim_%s as dim_id, sum(index_value) as v 
        from %s a, ad_manager.base_index c 
        where %s and c.id = %s and date_id between %s and %s 
        and index_id = c.numerator and c.is_accumulated=0 
        group by dim_id) aa, 
        (select dim_%s as dim_id, sum(index_value) as v  
        from %s a, ad_manager.base_index c 
        where %s and c.id = %s and date_id between %s and %s
        and index_id = c.denominator and c.is_accumulated=0 
        group by dim_id) bb 
        where aa.dim_id = bb.dim_id
        """%(distribution_dim, table_name, where_sql, distribution_index, begin_date_id, end_date_id,\
             distribution_dim, table_name, where_sql, distribution_index, begin_date_id, end_date_id,\
             distribution_dim, table_name, where_sql, distribution_index, begin_date_id, end_date_id))
        datas = cursor.fetchall()
        data_summary_dict2 = {}
        for data in datas:
            data_summary_dict2[data[0]] = data[1]
        day_summary_list =['汇总']
        for index_id in widget_config[widget_id]['index_list']:
            if index_id <> distribution_index:
                if index_id in data_summary_dict:
                    day_summary_list.append(data_summary_dict[index_id])
                else:
                    day_summary_list.append('-')
            else:
                for dim_value in widget_config[widget_id]['distribution_dim']['dim_value_list']:
                    if dim_value in data_summary_dict2:
                        day_summary_list.append(data_summary_dict2[dim_value])
                    else:
                        day_summary_list.append('-')
        return_list.append(day_summary_list)
            
        while begin_date <= end_date:
            date_id = int(begin_date.strftime('%Y%m%d'))
            day_list = [date_id]
            for index_id in widget_config[widget_id]['index_list']:
                if index_id <> distribution_index:
                    if (date_id, index_id) in data_dict:
                        day_list.append(data_dict[(date_id, index_id)])
                    else:
                        day_list.append('-')
                else:
                    for dim_value in widget_config[widget_id]['distribution_dim']['dim_value_list']:
                        if (date_id, dim_value) in data_dict2:
                            day_list.append(data_dict2[(date_id, dim_value)])
                        else:
                            day_list.append('-')
            return_list.append(day_list)
            begin_date+=datetime.timedelta(days=1)
            
    cursor.connection.close()
    cursor.close()
    return widget_config[widget_id]['table_head_list'], return_list
