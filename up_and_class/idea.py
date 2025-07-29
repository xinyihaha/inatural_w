"""
iNaturalist图片上传和分类API使用说明

1. 通过上传接口获取图片id
   接口：https://www.inaturalist.org/photos

2. 通过分类接口：https://api.inaturalist.org/v1/computervision/score_image
   获取分类：
   返回字典：common_ancestor
       score：得分
       分类：taxon
           记录：ancestor_ids这个分类list[[48460, 1, 47120, 372739, 47158, 184884, 47157, 47214, 145552, 876427]]
           里面从属倒排序，对应树：ancestry "48460/1/47120/372739/47158/184884/47157/47214/145552"
           id： 876427 
           preferred_common_name: "束带蛾属"

3. 通过下列接口获取分类信息
   接口：https://pyinaturalist.readthedocs.io/en/stable/modules/pyinaturalist.v1.taxa.html#pyinaturalist.v1.taxa.get_taxa_by_id
"""
