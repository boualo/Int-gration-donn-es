 val rowsRdd  : RDD[Row] = sc.parallelize(…) 
      val schema = StructType( 
StructField("field_1", Type_Field_1, nullable = [True or False] ), 
StructField("field_2", Type_Field_2, nullable = [True or False] ), 
      )      
      sc.createDataFrame(rowsRdd, schema)