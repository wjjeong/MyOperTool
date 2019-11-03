SELECT_MY_TAB_COLUMN = """ SELECT table_name,column_name,ordinal_position,column_type
                          FROM information_schema.COLUMNS a
                         WHERE table_schema in ('mdw','mdw2')
                           AND length(TABLE_NAME) = 6
                           and A.table_name = '{0}' """

SELECT_MY_IND_COLUMN = """ SELECT   index_name
                                ,column_name
                                ,seq_in_index
                           FROM INFORMATION_SCHEMA.STATISTICS a
                          WHERE 1=1
                            AND table_schema = 'mdw'
                            AND (INDEX_NAME LIKE '%ux_1' AND SUBSTR(table_NAME,1,2) IN ('AD','MP','CN','CI','GM','MA','IA','SA','FA','CP') AND LENGTH(INDEX_NAME) = 11
                                  OR INDEX_NAME LIKE '%idx_1' AND SUBSTR(table_NAME,1,2) NOT IN ('AD','MP','CN','CI','GM','MA','IA','SA','FA','CP') AND LENGTH(INDEX_NAME) = 12 )
                            and A.table_name = '{0}'
                          order by column_name,SEQ_IN_INDEX"""


SELECT_ORA_TAB_COLUMN = """SELECT TABLE_NAME
                                  ,column_name     
                                  ,column_id
                                  ,CASE WHEN DATA_type = 'VARCHAR2' THEN 'VARCHAR('||DATA_LENGTH||')' 
                                        WHEN DATA_type = 'NUMBER'   THEN 'DECIMAL('||DATA_PRECISION||','||DATA_SCALE||')'
                                        ELSE DATA_TYPE END column_type
                                  
                              FROM all_tab_columns A
                             WHERE owner = 'SCM'
                               and A.table_name = '{0}'
                             order by column_id"""


SELECT_ORA_IND_COLUMN = """ select index_name
                                  ,column_name
                                  ,column_position 
                              from all_ind_columns a
                             where table_owner = 'SCM'   
                               and index_name like '%PK'
                               and A.table_name = '{0}'
                             order by column_name,COLUMN_POSITION"""

SELECT_MY_CRE_IND = """select  'create index '|| table_name||'_idx_1 '||' on '||table_name||'('||listagg(column_name,',') WITHIN GROUP (ORDER BY COLUMN_POSITION)||');' ind_cre_script
                              ,'drop index '||table_name||'_idx_1 on '||table_name||';' ind_drop_script
                          from all_ind_columns a
                         where table_owner = 'SCM'      
                           and index_name like '%PK'
                           and A.table_name = '{0}'
                         group by table_name """


SELECT_MY_SCM_TAB_COLUMN = """SELECT '{0}' as sch_gb,table_name,column_name,ordinal_position,column_type,is_nullable,column_default
                                FROM information_schema.COLUMNS a
                               where A.table_schema = '{1}'
                               ORDER BY TABLE_NAME,COLUMN_NAME,ordinal_position  """



CREATE_SQLT_TAB1 = """create table if not exists schema_total_info
                        (
                         std_tab_name
                        ,std_col_name
                        ,std_col_ord
                        ,dev_col_ord
                        ,dev_col_type
                        ,dev_col_nn
                        ,dev_col_dv
                        ,qa_col_ord
                        ,qa_col_type
                        ,qa_col_nn
                        ,qa_col_dv
                        ,prod_col_ord
                        ,prod_col_type
                        ,prod_col_nn
                        ,prod_col_dv
                        ) """

CREATE_SQLT_TAB2 = """create table if not exists  schema_info
                            (
                             schema_gb
                            ,tab_name
                            ,col_name
                            ,col_ord
                            ,col_type
                            ,col_nn
                            ,col_dv
                            ) """



DELETE_SQLT_TAB1 = """delete from schema_total_info"""

DELETE_SQLT_TAB2 = """delete from schema_info """

INSERT_SQLT_TAB1 = """INSERT INTO schema_info ( schema_gb,tab_name,col_name,col_ord,col_type,col_nn,col_dv) VALUES (?,?,?,?,?,?,?)"""

INSERT_SQLT_TAB2 = """insert into schema_info (schema_gb,tab_name,col_name,col_ord) 
                         select 'std' schema_gb , tab_name,col_name,min(col_ord) col_ord 
                          from schema_info a
                         group by tab_name,col_name"""

INSERT_SQLT_TAB3 = """insert into schema_total_info
                         select a.tab_name,a.col_name,a.col_ord
                               ,b.col_ord,b.col_type,b.col_nn,b.col_dv
                               ,c.col_ord,c.col_type,c.col_nn,c.col_dv
                               ,d.col_ord,d.col_type,d.col_nn,d.col_dv
                          from schema_info a left outer join schema_info b on a.tab_name = b.tab_name and a.col_name = b.col_name and b.schema_gb = 'dev' 
                                             left outer join schema_info c on a.tab_name = c.tab_name and a.col_name = c.col_name and c.schema_gb = 'qa'
                                             left outer join schema_info d on a.tab_name = d.tab_name and a.col_name = d.col_name and d.schema_gb = 'prod'
                         where a.schema_gb = 'std'
                           and (b.tab_name is null or c.tab_name is null or d.tab_name is null)
                           and LENGTH(a.tab_name) = 6"""


SELECT_SQLT_SCM_DIFF = """SELECT *
                          FROM schema_total_info a
                        order by 1,3,2 """


SELECT_DAILY_CHECK = """SELECT @@hostname as CON_RESULT """

