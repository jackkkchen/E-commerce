"""
目前只写好了生成临时视图的 SQL 语句，还需要将其封装成函数，方便调用。

-- 用户输入的分类名称，例如 '家用电器'
SET @input_category = '2200W平面双灶';

-- 递归查询分类及其子分类
WITH RECURSIVE category_tree AS (
    -- 基础部分：获取用户输入的分类信息
    SELECT
        分类序号,
        分类名称,
        上级分类序号
    FROM
        product_cate_organized
    WHERE
        分类名称 = @input_category

    UNION ALL

    -- 递归部分：获取所有子分类
    SELECT
        pc.分类序号,
        pc.分类名称,
        pc.上级分类序号
    FROM
        product_cate_organized AS pc
    INNER JOIN
        category_tree AS ct
    ON
        pc.上级分类序号 = ct.分类序号
)

-- 查询结果：获取该分类及其子分类下的所有商品信息
SELECT
    p.*,
    ct.分类名称 AS 所属分类名称
FROM
    product AS p
JOIN
    category_tree AS ct
ON
    p.商品分类 = ct.分类名称;

"""