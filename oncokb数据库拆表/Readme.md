这是从monogodb中导出的数据
将数据导入到sqlite中
并使用django的orm进行数据操作
因此需要对其拆表，由于sql不精，这里将其用pandas拆分为四个csv，再导入到sqlite中
